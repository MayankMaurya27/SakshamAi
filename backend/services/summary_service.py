"""Summary generation service."""

import logging

from sqlalchemy.orm import Session

from ai.llm import get_llm
from ai.prompt_builder import build_prompt, format_retrieved_chunks
from config.constants import LearningMode
from database.repositories import ChunkRepository, DocumentRepository
from exceptions import DocumentNotFoundError

logger = logging.getLogger(__name__)


def get_summary(
    document_id: int,
    db: Session,
    regenerate: bool = False,
) -> dict:
    """
    Return stored summary or regenerate from document chunks.

    Returns:
        Dict with summary and optional key_points.
    """
    doc_repo = DocumentRepository(db)
    document = doc_repo.get_by_id(document_id)
    if document is None:
        raise DocumentNotFoundError(f"Document {document_id} not found.")

    if document.summary and not regenerate:
        import json

        key_concepts = []
        if document.key_concepts:
            try:
                key_concepts = json.loads(document.key_concepts)
            except json.JSONDecodeError:
                pass
        return {"summary": document.summary, "key_points": key_concepts}

    chunks = ChunkRepository(db).get_by_document_id(document_id)
    if not chunks:
        return {"summary": "No content available for summary.", "key_points": []}

    chunk_texts = [c.chunk_text for c in chunks[:5]]
    retrieved_context = format_retrieved_chunks(chunk_texts)

    prompt = build_prompt(LearningMode.SUMMARY, retrieved_context=retrieved_context)
    summary = get_llm().generate(prompt)

    logger.info("Generated summary for document_id=%d (regenerate=%s)", document_id, regenerate)
    return {"summary": summary, "key_points": []}
