"""Prepare chapter/document text for quiz generation."""

from __future__ import annotations

import re

from ai.context_cleaner import clean_context_for_llm, clean_context_text, trim_context_chunks
from ai.retriever import _is_low_quality_chunk
from config.settings import get_settings

settings = get_settings()

_NUMBERED_ITEM = re.compile(r"\b\d+\.\s+[A-Z\u0900-\u097F]")
_EXERCISE_LIST = re.compile(
    r"(?:\d+\.\s+[A-Z\u0900-\u097F][^.!?]{8,}[.!?]?\s*){3,}",
)


def is_exercise_list_chunk(text: str) -> bool:
    """Detect end-of-chapter exercise blocks that make poor quiz sources."""
    cleaned = clean_context_text(text)
    if not cleaned:
        return False
    numbered = _NUMBERED_ITEM.findall(cleaned)
    if len(numbered) >= 3 and _EXERCISE_LIST.search(cleaned):
        return True
    if len(numbered) >= 5:
        return True
    return False


def filter_quiz_source_chunks(chunks: list[str], subject: str | None = None) -> list[str]:
    """Drop low-quality and exercise-list chunks before quiz generation."""
    from services.quiz_math import filter_math_quiz_chunks, is_math_subject

    if is_math_subject(subject):
        chunks = filter_math_quiz_chunks(chunks)

    filtered: list[str] = []
    for chunk in chunks:
        if not chunk or not chunk.strip():
            continue
        if _is_low_quality_chunk(chunk):
            continue
        if is_exercise_list_chunk(chunk):
            continue
        cleaned = clean_context_for_llm(clean_context_text(chunk))
        if cleaned and len(cleaned) >= 80:
            filtered.append(cleaned)
    return filtered


def stratified_sample_chunks(chunks: list[str], max_chunks: int) -> list[str]:
    """Evenly sample chunks when the full chapter exceeds the context budget."""
    if len(chunks) <= max_chunks:
        return chunks
    if max_chunks <= 0:
        return []
    if max_chunks == 1:
        return [chunks[len(chunks) // 2]]

    step = (len(chunks) - 1) / (max_chunks - 1)
    indices = [round(i * step) for i in range(max_chunks)]
    seen: set[int] = set()
    sampled: list[str] = []
    for idx in indices:
        if idx not in seen:
            seen.add(idx)
            sampled.append(chunks[idx])
    return sampled


def _join_context_chunks(chunks: list[str], max_chars: int) -> str:
    """Join chunks with separators while staying within the character budget."""
    separator = "\n\n---\n\n"
    selected: list[str] = []
    used = 0
    for chunk in chunks:
        prefix_len = len(separator) if selected else 0
        if used + prefix_len + len(chunk) <= max_chars:
            selected.append(chunk)
            used += prefix_len + len(chunk)
            continue
        remaining = max_chars - used - prefix_len
        if remaining >= 250:
            snippet = chunk[:remaining].rsplit(" ", 1)[0].strip()
            if snippet:
                selected.append(snippet + "...")
        break
    return separator.join(selected)


def prepare_quiz_context(
    chunks: list[str],
    max_chars: int | None = None,
    subject: str | None = None,
) -> str:
    """
    Clean, filter, and trim chapter/document chunks into one quiz context string.

    Uses full chapter order when it fits; otherwise stratified sampling by chunk count.
    """
    budget = max_chars or settings.quiz_max_context_chars
    usable = filter_quiz_source_chunks(chunks, subject=subject)
    if not usable:
        usable = [
            clean_context_for_llm(clean_context_text(chunk))
            for chunk in chunks
            if chunk and chunk.strip()
        ]

    trimmed = trim_context_chunks(usable, max_chars=budget)
    if trimmed:
        return _join_context_chunks(trimmed, budget)

    avg_chunk_len = max(1, sum(len(chunk) for chunk in usable) // max(len(usable), 1))
    max_chunks = max(1, budget // avg_chunk_len)
    sampled = stratified_sample_chunks(usable, max_chunks)
    trimmed = trim_context_chunks(sampled, max_chars=budget)
    return _join_context_chunks(trimmed, budget) if trimmed else ""
