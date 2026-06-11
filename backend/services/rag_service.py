"""Core RAG service for question answering."""

import logging

from sqlalchemy.orm import Session

from ai.llm import get_llm
from ai.prompt_builder import build_fallback_prompt, build_prompt, format_retrieved_chunks
from ai.retriever import retrieve_document_context, retrieve_saksham_context
from config.constants import LearningMode, SourceType
from exceptions import DocumentNotFoundError, ValidationError
from services.accessibility_service import resolve_mode
from services.knowledge_service import validate_saksham_chapter

logger = logging.getLogger(__name__)


def _resolve_chapter(chapter: str | None, topic: str | None) -> str | None:
    """Resolve chapter from chapter or legacy topic field."""
    return chapter or topic


def answer_question(
    question: str,
    source: SourceType,
    db: Session,
    document_id: int | None = None,
    class_level: int | None = None,
    subject: str | None = None,
    topic: str | None = None,
    chapter: str | None = None,
    mode: LearningMode = LearningMode.LEARN,
    accessibility_profile=None,
) -> str:
    """
    Answer a question using RAG retrieval and LLM generation.

    Args:
        question: User question.
        source: document or saksham knowledge base.
        db: Database session.
        document_id: Required for document-scoped queries.
        class_level: Class level for Saksham queries.
        subject: Subject for Saksham queries.
        topic: Legacy chapter reference (use chapter instead).
        chapter: Chapter id or title for Saksham queries.
        mode: Learning mode for prompt selection.
        accessibility_profile: Optional accessibility override.

    Returns:
        Generated answer string.
    """
    if not question.strip():
        raise ValidationError("Question cannot be empty.")

    effective_mode = resolve_mode(mode, accessibility_profile)
    chapter_ref = _resolve_chapter(chapter, topic)

    if source == SourceType.DOCUMENT:
        if document_id is not None:
            from database.repositories import DocumentRepository

            doc = DocumentRepository(db).get_by_id(document_id)
            if doc is None:
                raise DocumentNotFoundError(f"Document {document_id} not found.")
        contexts = retrieve_document_context(question, db, document_id=document_id)
    else:
        if class_level is None or not subject or not chapter_ref:
            raise ValidationError(
                "class_level, subject, and chapter (or topic) are required for saksham source."
            )

        chapter_meta = validate_saksham_chapter(class_level, subject, chapter_ref)
        effective_mode = LearningMode.LEARN_FROM_SAKSHAM

        contexts = retrieve_saksham_context(
            question,
            class_level=class_level,
            subject=subject,
            chapter_ref=chapter_ref,
        )

    if not contexts:
        logger.info("No retrieval results; returning fallback response")
        return build_fallback_prompt()

    chunk_texts = [ctx.text for ctx in contexts]
    retrieved_context = format_retrieved_chunks(chunk_texts)

    prompt = build_prompt(
        effective_mode,
        retrieved_context=retrieved_context,
        question=question,
        topic=chapter_ref or "",
        grade=class_level or 8,
    )

    answer = get_llm().generate(prompt)
    logger.info("Generated answer for source=%s mode=%s", source.value, effective_mode.value)
    return answer
