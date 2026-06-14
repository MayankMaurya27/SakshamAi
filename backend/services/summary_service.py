"""Summary generation service for Saksham chapters and uploaded documents."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from ai.llm import get_llm
from ai.prompt_builder import build_summary_expand_prompt, build_summary_prompt
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
from services.summary_grounded import build_fallback_summary, build_minimal_source_summary
from services.summary_factual import ground_summary_text
from services.summary_parser import (
    clean_summary_text,
    count_paragraphs,
    count_words,
    merge_partial_summaries,
)

logger = logging.getLogger(__name__)
settings = get_settings()
SUMMARY_FORMAT_VERSION = "v2-prose"


def _resolve_chapter(chapter: str | None, topic: str | None) -> str | None:
    return chapter or topic


def _is_short_corpus(corpus: str) -> bool:
    return len(corpus.strip()) < 500


def _word_targets(context_chars: int) -> tuple[int, int, int]:
    """Return min_words, target_words, min_paragraphs for a context size."""
    if context_chars < 500:
        return 20, 50, 1
    if context_chars < 2000:
        return 120, 180, 3
    if context_chars < 4500:
        return 200, 280, 4
    return settings.summary_min_words, settings.summary_target_words, settings.summary_min_paragraphs


def _needs_map_reduce(chunks: list[str], subject: str | None = None) -> bool:
    usable = filter_summary_source_chunks(chunks, subject=subject)
    context = prepare_summary_context(usable or chunks, subject=subject)
    return len(context) > settings.summary_max_context_chars


def _is_usable_summary(summary: str, min_words: int, min_paragraphs: int) -> bool:
    cleaned = summary.strip()
    return (
        bool(cleaned)
        and count_words(cleaned) >= min_words
        and count_paragraphs(cleaned) >= min_paragraphs
    )


def _generate_summary_text(
    context: str,
    topic: str = "",
    grade: int = 8,
    window_hint: str = "",
    mode: str = "full",
    target_words: int | None = None,
    min_paragraphs: int | None = None,
) -> str:
    if not context.strip():
        return ""

    min_words, default_target, default_paragraphs = _word_targets(len(context))
    resolved_target = target_words or default_target
    resolved_paragraphs = min_paragraphs or default_paragraphs

    prompt = build_summary_prompt(
        context,
        topic=topic,
        grade=grade,
        window_hint=window_hint,
        mode=mode,
        target_words=resolved_target,
        min_paragraphs=resolved_paragraphs,
    )
    raw = get_llm().generate(prompt, num_predict=settings.ollama_num_predict_summary)
    return clean_summary_text(raw)


def _source_corpus(chunks: list[str], subject: str | None = None) -> str:
    usable = filter_summary_source_chunks(chunks, subject=subject)
    source = usable if usable else [chunk.strip() for chunk in chunks if chunk.strip()]
    return "\n".join(source)


def _expand_summary_if_needed(
    summary: str,
    context: str,
    topic: str,
    grade: int,
    min_words: int,
    target_words: int,
    min_paragraphs: int,
) -> str:
    if count_words(summary) >= min_words and count_paragraphs(summary) >= min_paragraphs:
        return summary

    prompt = build_summary_expand_prompt(
        summary,
        context,
        topic=topic,
        grade=grade,
        target_words=target_words,
        min_paragraphs=min_paragraphs,
    )
    expanded = clean_summary_text(
        get_llm().generate(prompt, num_predict=settings.ollama_num_predict_summary)
    )
    if count_words(expanded) >= count_words(summary):
        return expanded
    return summary


def _resolve_fallback_summary(
    source_chunks: list[str],
    corpus: str,
    topic: str,
) -> str:
    if _is_short_corpus(corpus):
        return build_minimal_source_summary(source_chunks, topic)
    return ground_summary_text(
        build_fallback_summary(source_chunks, chapter_title=topic)["summary"],
        corpus,
    )


def _finalize_summary(
    summary: str,
    context: str,
    corpus: str,
    topic: str,
    grade: int,
    min_words: int,
    target_words: int,
    min_paragraphs: int,
    source_chunks: list[str] | None = None,
) -> str:
    cleaned = ground_summary_text(clean_summary_text(summary), corpus)
    if not _is_usable_summary(cleaned, min_words, min_paragraphs) and not _is_short_corpus(
        corpus
    ):
        cleaned = _expand_summary_if_needed(
            cleaned or summary,
            context,
            topic,
            grade,
            min_words,
            target_words,
            min_paragraphs,
        )
    cleaned = ground_summary_text(clean_summary_text(cleaned), corpus)
    if not cleaned.strip() and source_chunks:
        cleaned = build_minimal_source_summary(source_chunks, topic)
    return cleaned


def _generate_from_chunks(
    chunks: list[str],
    topic: str = "",
    grade: int = 8,
    subject: str | None = None,
) -> dict[str, Any]:
    usable = filter_summary_source_chunks(chunks, subject=subject)
    source_chunks = usable if usable else [chunk for chunk in chunks if chunk.strip()]
    corpus = _source_corpus(chunks, subject=subject)

    if not source_chunks:
        return {
            "summary": "No content available for summary.",
            "format_version": SUMMARY_FORMAT_VERSION,
        }

    full_context = prepare_summary_context(chunks, subject=subject)
    min_words, target_words, min_paragraphs = _word_targets(len(full_context))

    if not _needs_map_reduce(chunks, subject=subject):
        summary = _generate_summary_text(
            full_context,
            topic=topic,
            grade=grade,
            mode="full",
            target_words=target_words,
            min_paragraphs=min_paragraphs,
        )
        summary = _finalize_summary(
            summary,
            full_context,
            corpus,
            topic,
            grade,
            min_words,
            target_words,
            min_paragraphs,
            source_chunks=source_chunks,
        )
        if not _is_usable_summary(summary, min_words, min_paragraphs):
            summary = _resolve_fallback_summary(source_chunks, corpus, topic)
        if not summary.strip():
            summary = build_minimal_source_summary(source_chunks, topic)
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
            target_words=max(180, target_words // max(1, len(windows))),
            min_paragraphs=max(3, min_paragraphs // 2),
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
            target_words=target_words,
            min_paragraphs=min_paragraphs + 1,
        )

    if not _is_usable_summary(summary, min_words, min_paragraphs):
        summary = merge_partial_summaries(partials)

    summary = _finalize_summary(
        summary,
        full_context,
        corpus,
        topic,
        grade,
        min_words,
        target_words,
        min_paragraphs,
        source_chunks=source_chunks,
    )

    if not _is_usable_summary(summary, min_words, min_paragraphs):
        summary = _resolve_fallback_summary(source_chunks, corpus, topic)

    if not summary.strip():
        summary = build_minimal_source_summary(source_chunks, topic)

    return {"summary": summary, "format_version": SUMMARY_FORMAT_VERSION}


def _document_payload_from_db(document) -> dict[str, Any] | None:
    if not document.summary:
        return None
    return {
        "summary": document.summary,
        "format_version": SUMMARY_FORMAT_VERSION,
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

    parsed = generate_summary_from_chunks(
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
        "Generated Saksham summary: class=%s subject=%s chapter=%s words=%d",
        class_level,
        subject,
        chapter_id,
        count_words(payload.get("summary", "")),
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

    return save_document_summary_from_chunks(
        document_id,
        chunk_texts,
        db,
        title=document.filename,
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


def generate_summary_from_chunks(
    chunk_texts: list[str],
    topic: str = "",
    grade: int = 8,
    subject: str | None = None,
) -> dict[str, Any]:
    """Shared summary pipeline for Saksham chapters and uploaded documents."""
    return _generate_from_chunks(
        chunk_texts,
        topic=topic,
        grade=grade,
        subject=subject,
    )


def save_document_summary_from_chunks(
    document_id: int,
    chunk_texts: list[str],
    db: Session,
    title: str = "",
    grade: int = 8,
) -> dict[str, Any]:
    """Run the shared summary pipeline and persist results for an uploaded document."""
    parsed = generate_summary_from_chunks(
        chunk_texts,
        topic=title,
        grade=grade,
    )
    DocumentRepository(db).update_analysis(
        document_id,
        parsed.get("summary", ""),
        [],
    )
    return _build_response_payload(
        parsed,
        SourceType.DOCUMENT,
        document_id=document_id,
    )


def build_document_summary_from_chunks(
    chunk_texts: list[str],
    title: str = "",
    grade: int = 8,
) -> dict[str, Any]:
    """Backward-compatible alias for upload and legacy callers."""
    return generate_summary_from_chunks(chunk_texts, topic=title, grade=grade)
