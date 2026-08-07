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

        options = q.get("options", {})

        option_a = ""
        option_b = ""
        option_c = ""
        option_d = ""

        if isinstance(options, dict):
            option_a = options.get("A", "")
            option_b = options.get("B", "")
            option_c = options.get("C", "")
            option_d = options.get("D", "")

        elif isinstance(options, list):
            option_a = options[0] if len(options) > 0 else ""
            option_b = options[1] if len(options) > 1 else ""
            option_c = options[2] if len(options) > 2 else ""
            option_d = options[3] if len(options) > 3 else ""

        normalized.append(
            {
                "question": q.get("question", ""),
                "option_a": q.get("option_a", option_a),
                "option_b": q.get("option_b", option_b),
                "option_c": q.get("option_c", option_c),
                "option_d": q.get("option_d", option_d),
                "correct_answer": str(
                    q.get("correct_answer", "A")
                )[0].upper(),
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

    Summary uses the same grounded prose pipeline as Learn from Saksham via
    `save_document_summary_from_chunks()` → `generate_summary_from_chunks()`.
    Quiz questions still come from a separate AUTO_ANALYSIS JSON call.

    Returns:
        Dict with document_id, summary, format_version, key_concepts, quiz_count.
    """
    if len(file_content) == 0:
        raise PDFProcessingError("Uploaded file is empty.")

    safe_filename = _sanitize_filename(original_filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_filename}"
    filepath = settings.uploads_dir / unique_name
    document = None

    try:
        filepath.write_bytes(file_content)

        text, page_count = extract_text(str(filepath))
        chunks = create_chunks(text)

        if not chunks:
            raise PDFProcessingError("Could not create text chunks from PDF.")

        doc_repo = DocumentRepository(db)
        document = doc_repo.create(filename=safe_filename, filepath=str(filepath))

        user_index = get_user_index()
        faiss_ids = index_document(
            chunks,
            user_index,
            metadata_base={"source": "user_document", "document_id": document.id},
        )
        save_user_index()

        chunk_records = [
            (idx, chunk_text, faiss_id)
            for idx, (chunk_text, faiss_id) in enumerate(zip(chunks, faiss_ids))
        ]
        ChunkRepository(db).create_batch(document.id, chunk_records)

        # Performance/stability optimization on edge platform (Jetson):
        # Instead of calling the slow local LLM synchronously to generate summary and quiz questions
        # during upload (which takes 3+ minutes and times out the tunnel with 502), we skip
        # the generation here. The summary and quiz questions will be generated lazily
        # on-demand when the student visits those sections.
        logger.info(
            "Processed upload: document_id=%d, pages=%d, chunks=%d (lazy summary/quiz enabled)",
            document.id,
            page_count,
            len(chunks),
        )

        return {
            "document_id": document.id,
            "summary": "",
            "format_version": "v1",
            "key_concepts": [],
            "quiz_count": 0,
        }
    except Exception:
        if document is not None:
            from services.document_service import delete_document

            try:
                delete_document(document.id, db)
            except Exception:
                DocumentRepository(db).delete_by_id(document.id)
                if filepath.exists():
                    filepath.unlink(missing_ok=True)
        elif filepath.exists():
            filepath.unlink(missing_ok=True)
        raise
