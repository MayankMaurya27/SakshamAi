"""Quiz generation service."""

import json
import logging

from sqlalchemy.orm import Session

from ai.llm import get_llm
from ai.prompt_builder import build_prompt, format_retrieved_chunks
from config.constants import LearningMode
from database.repositories import ChunkRepository, DocumentRepository, QuizRepository
from exceptions import DocumentNotFoundError

logger = logging.getLogger(__name__)


def _parse_quiz_response(response: str) -> list[dict]:
    """Parse quiz JSON from LLM response."""
    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(response[start:end])
            questions = data.get("questions", data if isinstance(data, list) else [])
            return questions if isinstance(questions, list) else []
    except json.JSONDecodeError:
        pass
    return []


def _normalize_questions(raw: list) -> list[dict]:
    """Normalize quiz question format."""
    normalized = []
    for q in raw:
        if not isinstance(q, dict):
            continue
        normalized.append(
            {
                "question": q.get("question", ""),
                "options": {
                    "A": q.get("option_a", q.get("options", {}).get("A", "")),
                    "B": q.get("option_b", q.get("options", {}).get("B", "")),
                    "C": q.get("option_c", q.get("options", {}).get("C", "")),
                    "D": q.get("option_d", q.get("options", {}).get("D", "")),
                },
                "correct_answer": str(q.get("correct_answer", "A"))[0].upper(),
            }
        )
    return [q for q in normalized if q["question"]]


def get_quiz(
    document_id: int,
    db: Session,
    regenerate: bool = False,
) -> dict:
    """
    Return stored quiz or regenerate from document chunks.

    Returns:
        Dict with questions list.
    """
    doc_repo = DocumentRepository(db)
    document = doc_repo.get_by_id(document_id)
    if document is None:
        raise DocumentNotFoundError(f"Document {document_id} not found.")

    quiz_repo = QuizRepository(db)

    if not regenerate:
        existing = quiz_repo.get_by_document_id(document_id)
        if existing:
            return {"questions": quiz_repo.to_dict_list(existing)}

    chunks = ChunkRepository(db).get_by_document_id(document_id)
    if not chunks:
        return {"questions": []}

    chunk_texts = [c.chunk_text for c in chunks[:5]]
    retrieved_context = format_retrieved_chunks(chunk_texts)

    prompt = build_prompt(LearningMode.QUIZ, retrieved_context=retrieved_context)
    response = get_llm().generate(prompt)
    raw_questions = _parse_quiz_response(response)
    questions = _normalize_questions(raw_questions)

    if questions and regenerate:
        quiz_repo.delete_by_document_id(document_id)
        store_data = [
            {
                "question": q["question"],
                "option_a": q["options"]["A"],
                "option_b": q["options"]["B"],
                "option_c": q["options"]["C"],
                "option_d": q["options"]["D"],
                "correct_answer": q["correct_answer"],
            }
            for q in questions
        ]
        quiz_repo.create_batch(document_id, store_data)

    logger.info(
        "Quiz for document_id=%d: %d questions (regenerate=%s)",
        document_id,
        len(questions),
        regenerate,
    )
    return {"questions": questions}
