"""Document upload processing orchestration."""

import json
import logging
import re
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from ai.faiss_manager import get_user_index, save_user_index
from ai.llm import get_llm
from ai.prompt_builder import build_prompt
from config.constants import LearningMode, MAX_AUTO_ANALYSIS_TOKENS
from config.settings import get_settings
from database.repositories import ChunkRepository, DocumentRepository, QuizRepository
from documents.chunker import create_chunks, truncate_to_tokens
from documents.indexer import index_document
from documents.pdf_parser import extract_text
from exceptions import PDFProcessingError

logger = logging.getLogger(__name__)
settings = get_settings()


def _sanitize_filename(filename: str) -> str:
    """Remove path traversal and unsafe characters from filename."""
    name = Path(filename).name
    name = re.sub(r"[^\w.\-]", "_", name)
    if not name.lower().endswith(".pdf"):
        name = f"{name}.pdf"
    return name


def _parse_auto_analysis(response: str) -> dict:
    """Parse LLM auto-analysis JSON response with fallback."""
    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except json.JSONDecodeError:
        pass

    return {
        "summary": response[:500] if response else "Summary not available.",
        "key_concepts": [],
        "questions": [],
    }


def _normalize_questions(raw_questions: list) -> list[dict[str, str]]:
    """Normalize quiz questions from LLM output."""
    normalized: list[dict[str, str]] = []
    for q in raw_questions[:5]:
        if not isinstance(q, dict):
            continue
        normalized.append(
            {
                "question": q.get("question", ""),
                "option_a": q.get("option_a", q.get("options", {}).get("A", "")),
                "option_b": q.get("option_b", q.get("options", {}).get("B", "")),
                "option_c": q.get("option_c", q.get("options", {}).get("C", "")),
                "option_d": q.get("option_d", q.get("options", {}).get("D", "")),
                "correct_answer": str(q.get("correct_answer", "A"))[0].upper(),
            }
        )
    return [q for q in normalized if q["question"]]


def process_upload(
    file_content: bytes,
    original_filename: str,
    db: Session,
) -> dict:
    """
    Process an uploaded PDF through the full pipeline.

    Returns:
        Dict with document_id, summary, key_concepts, quiz_count.
    """
    if len(file_content) == 0:
        raise PDFProcessingError("Uploaded file is empty.")

    safe_filename = _sanitize_filename(original_filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_filename}"
    filepath = settings.uploads_dir / unique_name
    filepath.write_bytes(file_content)

    text, page_count = extract_text(str(filepath))
    chunks = create_chunks(text)

    if not chunks:
        raise PDFProcessingError("Could not create text chunks from PDF.")

    user_index = get_user_index()
    faiss_ids = index_document(
        chunks,
        user_index,
        metadata_base={"source": "user_document"},
    )
    save_user_index()

    doc_repo = DocumentRepository(db)
    document = doc_repo.create(filename=safe_filename, filepath=str(filepath))

    chunk_records = [
        (idx, chunk_text, faiss_id)
        for idx, (chunk_text, faiss_id) in enumerate(zip(chunks, faiss_ids))
    ]
    ChunkRepository(db).create_batch(document.id, chunk_records)

    from services.summary_service import build_document_summary_from_chunks

    summary_payload = build_document_summary_from_chunks(chunks, safe_filename)
    summary = summary_payload.get("summary", "")
    key_concepts: list = []

    truncated_text = truncate_to_tokens(text, MAX_AUTO_ANALYSIS_TOKENS)
    analysis_prompt = build_prompt(
        LearningMode.AUTO_ANALYSIS,
        document_text=truncated_text,
    )
    llm_response = get_llm().generate(analysis_prompt)
    analysis = _parse_auto_analysis(llm_response)

    doc_repo.update_analysis(document.id, summary, key_concepts)

    questions = _normalize_questions(analysis.get("questions", []))
    if questions:
        QuizRepository(db).create_batch(document.id, questions)

    logger.info(
        "Processed upload: document_id=%d, pages=%d, chunks=%d, quizzes=%d",
        document.id,
        page_count,
        len(chunks),
        len(questions),
    )

    return {
        "document_id": document.id,
        "summary": summary,
        "key_concepts": key_concepts,
        "quiz_count": len(questions),
    }
