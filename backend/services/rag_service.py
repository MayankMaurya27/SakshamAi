"""Core RAG service for question answering."""

import logging

from sqlalchemy.orm import Session

from ai.activity_formatter import ActivityIntent, detect_activity_intent, try_format_activity_answer
from ai.answer_formatter import format_student_answer
from ai.bio_formatter import is_bio_question, try_format_bio_answer
from ai.context_cleaner import clean_context_for_llm, clean_context_text, trim_context_chunks
from config.settings import get_settings
from ai.llm import get_llm
from ai.prompt_builder import build_fallback_prompt, build_prompt, format_retrieved_chunks
from ai.question_router import (
    context_char_limit,
    is_broad_concept_question,
    resolve_answer_profile,
    retrieval_top_k,
)
from ai.retriever import (
    extract_content_refs,
    extract_query_terms,
    retrieve_document_context,
    retrieve_saksham_context,
)
from config.constants import LearningMode, SourceType, AnswerProfile
from exceptions import DocumentNotFoundError, ValidationError
from services.accessibility_service import resolve_mode
from services.knowledge_service import validate_saksham_chapter

logger = logging.getLogger(__name__)
settings = get_settings()


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
    content_refs = extract_content_refs(question)
    activity_refs = [
        ref for ref in content_refs if ref.lower().startswith("activity")
    ]
    answer_profile = resolve_answer_profile(
        question,
        activity_refs=activity_refs,
        content_refs=content_refs,
    )
    broad_question = is_broad_concept_question(question)
    retrieval_k = retrieval_top_k(answer_profile, settings)

    if source == SourceType.DOCUMENT:
        if document_id is not None:
            from database.repositories import DocumentRepository

            doc = DocumentRepository(db).get_by_id(document_id)
            if doc is None:
                raise DocumentNotFoundError(f"Document {document_id} not found.")
        contexts = retrieve_document_context(
            question,
            db,
            document_id=document_id,
            top_k=retrieval_k,
        )
    else:
        if class_level is None or not subject or not chapter_ref:
            raise ValidationError(
                "class_level, subject, and chapter (or topic) are required for saksham source."
            )

        validate_saksham_chapter(class_level, subject, chapter_ref)

        contexts = retrieve_saksham_context(
            question,
            class_level=class_level,
            subject=subject,
            chapter_ref=chapter_ref,
            top_k=retrieval_k,
        )

    if not contexts:
        logger.info("No retrieval results; returning fallback response")
        return build_fallback_prompt()

    activity_passage: str | None = None
    activity_intent = ActivityIntent.FOCUS

    if activity_refs:
        activity_passage = clean_context_text(contexts[0].text)
        activity_intent = detect_activity_intent(question)
        if activity_intent != ActivityIntent.FOCUS:
            structured = try_format_activity_answer(
                activity_passage,
                activity_refs[0],
                intent=activity_intent,
            )
            if structured:
                logger.info(
                    "Returning structured %s answer for %s",
                    activity_intent.value,
                    activity_refs[0],
                )
                return structured

    max_context_chars = context_char_limit(answer_profile, settings)

    if activity_passage and activity_intent == ActivityIntent.FOCUS:
        chunk_texts = [clean_context_for_llm(activity_passage)]
        answer_profile = AnswerProfile.STRICT
    else:
        chunk_texts = [
            clean_context_for_llm(clean_context_text(ctx.text)) for ctx in contexts
        ]
        chunk_texts = trim_context_chunks(
            chunk_texts,
            max_chars=max_context_chars,
        )
    retrieved_context = format_retrieved_chunks(chunk_texts)

    if not activity_refs and is_bio_question(question):
        bio_answer = try_format_bio_answer(
            retrieved_context,
            extract_query_terms(question),
        )
        if bio_answer:
            logger.info("Returning structured biography answer from textbook profile")
            return bio_answer

    topic_label = chapter_ref or ""
    if source == SourceType.DOCUMENT and document_id is not None and not topic_label:
        from database.repositories import DocumentRepository

        doc = DocumentRepository(db).get_by_id(document_id)
        topic_label = doc.filename if doc else "Uploaded document"

    prompt = build_prompt(
        effective_mode,
        retrieved_context=retrieved_context,
        question=question,
        topic=topic_label,
        grade=class_level or 8,
        answer_profile=answer_profile,
        broad_question=broad_question,
    )

    raw_answer = get_llm().generate(prompt)
    answer = format_student_answer(raw_answer)
    logger.info(
        "Generated answer for source=%s mode=%s profile=%s broad=%s",
        source.value,
        effective_mode.value,
        answer_profile.value,
        broad_question,
    )
    return answer
