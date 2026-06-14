"""Summary generation service for Saksham chapters and uploaded documents."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from ai.llm import get_llm
from ai.prompt_builder import build_summary_prompt
from config.constants import SourceType
from config.settings import get_settings
from database.repositories import ChunkRepository, DocumentRepository
from exceptions import DocumentNotFoundError, ValidationError
from services.knowledge_service import (
    get_chapter_chunk_texts,
    validate_saksham_chapter,
)
from services.summary_cache import cache_path, load_cached_summary, save_cached_summary
from services.summary_context import (
    filter_summary_source_chunks,
    prepare_summary_context,
    sample_summary_windows,
)
from services.summary_grounded import build_fallback_summary
from services.summary_parser import (
    clean_summary_text,
    count_paragraphs,
    merge_partial_summaries,
)

logger = logging.getLogger(__name__)
settings = get_settings()
SUMMARY_FORMAT_VERSION = "v2-prose"


def _resolve_chapter(chapter: str | None, topic: str | None) -> str | None:
    return chapter or topic


def _needs_map_reduce(chunks: list[str], subject: str | None = None) -> bool:
    usable = filter_summary_source_chunks(chunks, subject=subject)
    context = prepare_summary_context(usable or chunks, subject=subject)
    return len(context) > settings.summary_max_context_chars


def _is_usable_summary(summary: str) -> bool:
    cleaned = summary.strip()
    return bool(cleaned) and len(cleaned) >= 80 and count_paragraphs(cleaned) >= 2


def _generate_summary_text(
    context: str,
    topic: str = "",
    grade: int = 8,
    window_hint: str = "",
    mode: str = "full",
) -> str:
    if not context.strip():
        return ""

    prompt = build_summary_prompt(
        context,
        topic=topic,
        grade=grade,
        window_hint=window_hint,
        mode=mode,
    )
    raw = get_llm().generate(prompt, num_predict=settings.ollama_num_predict_summary)
    return clean_summary_text(raw)


def _generate_from_chunks(
    chunks: list[str],
    topic: str = "",
    grade: int = 8,
    subject: str | None = None,
) -> dict[str, Any]:
    usable = filter_summary_source_chunks(chunks, subject=subject)
    source_chunks = usable if usable else [chunk for chunk in chunks if chunk.strip()]

    if not source_chunks:
        return {
            "summary": "No content available for summary.",
            "format_version": SUMMARY_FORMAT_VERSION,
        }

    if not _needs_map_reduce(chunks, subject=subject):
        context = prepare_summary_context(chunks, subject=subject)
        summary = _generate_summary_text(context, topic=topic, grade=grade, mode="full")
        if not _is_usable_summary(summary):
            summary = build_fallback_summary(source_chunks, chapter_title=topic)["summary"]
        return {"summary": summary, "format_version": SUMMARY_FORMAT_VERSION}

    windows = sample_summary_windows(chunks)[: settings.summary_map_reduce_windows]
    partials: list[str] = []
    for idx, window in enumerate(windows, start=1):
        context = prepare_summary_context(window, subject=subject)
        hint = f"This is part {idx} of {len(windows)} from the chapter."
        partial = _generate_summary_text(
            context,
            topic=topic,
            grade=grade,
            window_hint=hint,
            mode="partial",
        )
        if partial:
            partials.append(partial)

    summary = ""
    if partials:
        synthesis_context = "\n\n---\n\n".join(partials)
        summary = _generate_summary_text(
            synthesis_context,
            topic=topic,
            grade=grade,
            window_hint=f"Combine these {len(partials)} partial notes into one chapter summary.",
            mode="synthesis",
        )

    if not _is_usable_summary(summary):
        summary = merge_partial_summaries(partials)
    if not _is_usable_summary(summary):
        summary = build_fallback_summary(source_chunks, chapter_title=topic)["summary"]

    return {"summary": summary, "format_version": SUMMARY_FORMAT_VERSION}


def _document_payload_from_db(document) -> dict[str, Any] | None:
    if not document.summary:
        return None
    return {
        "summary": document.summary,
        "format_version": "v0-stored",
        "source": SourceType.DOCUMENT.value,
        "document_id": document.id,
        "cached": True,
    }


def _build_response_payload(
    parsed: dict[str, Any],
    source: SourceType,
    class_level: int | None = None,
    subject: str | None = None,
    chapter: str | None = None,
    chapter_id: str | None = None,
    document_id: int | None = None,
    cached: bool = False,
) -> dict[str, Any]:
    payload = dict(parsed)
    payload["source"] = source.value
    payload["cached"] = cached
    if source == SourceType.SAKSHAM:
        payload.update(
            {
                "class_level": class_level,
                "subject": subject,
                "chapter": chapter,
                "chapter_id": chapter_id,
            }
        )
    else:
        payload["document_id"] = document_id
    return payload


def generate_saksham_summary(
    class_level: int,
    subject: str,
    chapter_ref: str,
    regenerate: bool = False,
) -> dict[str, Any]:
    """Generate a revision summary for a Saksham curriculum chapter."""
    chapter = validate_saksham_chapter(class_level, subject, chapter_ref)
    chapter_id = chapter["chapter_id"]
    chapter_title = chapter.get("chapter_title") or chapter_ref

    cache_file = cache_path(
        SourceType.SAKSHAM.value,
        class_level=class_level,
        subject=subject,
        chapter_id=chapter_id,
    )
    if not regenerate:
        cached = load_cached_summary(cache_file)
        if cached:
            if (
                cached.get("chapter_id") == chapter_id
                and cached.get("class_level") == class_level
                and str(cached.get("subject", "")).lower() == subject.strip().lower()
            ):
                cached["cached"] = True
                return cached
            logger.warning(
                "Ignoring summary cache with mismatched metadata for chapter_id=%s",
                chapter_id,
            )

    chunks = get_chapter_chunk_texts(class_level, subject, chapter_ref)
    if not chunks:
        raise ValidationError(
            f"No indexed content for chapter '{chapter_ref}'. Run curriculum ingest."
        )

    parsed = _generate_from_chunks(
        chunks,
        topic=chapter_title,
        grade=class_level,
        subject=subject,
    )
    payload = _build_response_payload(
        parsed,
        SourceType.SAKSHAM,
        class_level=class_level,
        subject=subject,
        chapter=chapter_title,
        chapter_id=chapter_id,
    )
    save_cached_summary(cache_file, payload)
    logger.info(
        "Generated Saksham summary: class=%s subject=%s chapter=%s",
        class_level,
        subject,
        chapter_id,
    )
    return payload


def generate_document_summary(
    document_id: int,
    db: Session,
    regenerate: bool = False,
) -> dict[str, Any]:
    """Generate or return a stored summary for an uploaded document."""
    doc_repo = DocumentRepository(db)
    document = doc_repo.get_by_id(document_id)
    if document is None:
        raise DocumentNotFoundError(f"Document {document_id} not found.")

    if not regenerate:
        stored = _document_payload_from_db(document)
        if stored and stored.get("summary"):
            return stored

    chunks = ChunkRepository(db).get_by_document_id(document_id)
    chunk_texts = [chunk.chunk_text for chunk in chunks]
    if not chunk_texts:
        return _build_response_payload(
            {
                "summary": "No content available for summary.",
                "format_version": SUMMARY_FORMAT_VERSION,
            },
            SourceType.DOCUMENT,
            document_id=document_id,
        )

    parsed = _generate_from_chunks(chunk_texts, topic=document.filename, grade=8)
    doc_repo.update_analysis(document.id, parsed.get("summary", ""), [])
    return _build_response_payload(
        parsed,
        SourceType.DOCUMENT,
        document_id=document_id,
    )


def generate_summary(
    source: SourceType,
    db: Session,
    regenerate: bool = False,
    document_id: int | None = None,
    class_level: int | None = None,
    subject: str | None = None,
    chapter: str | None = None,
    topic: str | None = None,
) -> dict[str, Any]:
    """Unified summary entry point for Saksham and document sources."""
    chapter_ref = _resolve_chapter(chapter, topic)
    if source == SourceType.SAKSHAM:
        if class_level is None or not subject or not chapter_ref:
            raise ValidationError(
                "Saksham summary requires class_level, subject, and chapter."
            )
        return generate_saksham_summary(
            class_level,
            subject,
            chapter_ref,
            regenerate=regenerate,
        )

    if document_id is None:
        raise ValidationError("Document summary requires document_id.")
    return generate_document_summary(document_id, db, regenerate=regenerate)


def get_summary(
    document_id: int,
    db: Session,
    regenerate: bool = False,
) -> dict[str, Any]:
    """Backward-compatible document summary helper."""
    return generate_document_summary(document_id, db, regenerate=regenerate)


def build_document_summary_from_chunks(
    chunk_texts: list[str],
    title: str = "",
    grade: int = 8,
) -> dict[str, Any]:
    """Build a summary payload from indexed document chunks (upload pipeline)."""
    return _generate_from_chunks(chunk_texts, topic=title, grade=grade)
