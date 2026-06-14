"""Prepare chapter/document text for summary generation."""

from __future__ import annotations

import re

from ai.context_cleaner import clean_context_for_llm, clean_context_text
from config.settings import get_settings
from services.quiz_context import (
    filter_quiz_source_chunks,
    prepare_quiz_context,
    stratified_sample_chunks,
)

settings = get_settings()

_ACTIVITY_HEADER = re.compile(r"\bActivity\s+\d+(?:\.\d+)?\b", re.I)
_ACTIVITY_LINE = re.compile(
    r"^\s*(?:Activity\s+\d+(?:\.\d+)?|Aim|Procedure|Observation|Conclusion|"
    r"Let us (?:try|find out|explore|perform|discuss)|Take two|Mark a line|"
    r"Observe that|Perform the)\b",
    re.I | re.M,
)


_ACTIVITY_INSTRUCTION = re.compile(
    r"\b(?:Let us (?:try|find out|explore|perform|discuss)|Take two|Mark a line|"
    r"Observe that|Perform the)\b",
    re.I,
)
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _is_activity_sentence(sentence: str) -> bool:
    stripped = sentence.strip()
    if not stripped:
        return True
    if _ACTIVITY_HEADER.search(stripped):
        return True
    if _ACTIVITY_LINE.match(stripped):
        return True
    if _ACTIVITY_INSTRUCTION.search(stripped):
        return True
    return False


def strip_activity_passages(text: str) -> str:
    """Remove activity blocks and instruction lines from chunk text."""
    if not text.strip():
        return ""

    parts: list[str] = []
    last_end = 0
    for match in _ACTIVITY_HEADER.finditer(text):
        if match.start() > last_end:
            segment = text[last_end : match.start()]
            parts.append(segment)
        last_end = match.end()
        next_activity = _ACTIVITY_HEADER.search(text, last_end)
        stop = next_activity.start() if next_activity else len(text)
        block = text[last_end:stop]
        for sentence in _SENTENCE_SPLIT.split(block):
            if not _is_activity_sentence(sentence):
                parts.append(sentence.strip())
        last_end = stop

    if last_end < len(text):
        parts.append(text[last_end:])

    cleaned_parts: list[str] = []
    for part in parts:
        sentences: list[str] = []
        for sentence in _SENTENCE_SPLIT.split(part):
            stripped = sentence.strip()
            if not stripped or _is_activity_sentence(stripped):
                continue
            sentences.append(stripped)
        block = " ".join(sentences).strip()
        if block:
            cleaned_parts.append(block)

    merged = "\n".join(cleaned_parts)
    merged = re.sub(r"\n{3,}", "\n\n", merged).strip()
    return clean_context_for_llm(clean_context_text(merged))


def is_activity_heavy_chunk(text: str) -> bool:
    """True when a chunk is mostly activity instructions."""
    cleaned = clean_context_text(text)
    if not cleaned:
        return True
    activity_hits = len(_ACTIVITY_HEADER.findall(cleaned))
    if activity_hits >= 2:
        return True
    if activity_hits == 1 and len(cleaned) < 400:
        return True
    instruction_hits = sum(
        1 for line in cleaned.splitlines() if _ACTIVITY_LINE.match(line.strip())
    )
    return instruction_hits >= 4 and instruction_hits * 40 > len(cleaned)


def filter_summary_source_chunks(
    chunks: list[str],
    subject: str | None = None,
) -> list[str]:
    """Drop exercises, activities, and low-quality chunks before summarization."""
    filtered: list[str] = []
    for chunk in filter_quiz_source_chunks(chunks, subject=subject):
        if is_activity_heavy_chunk(chunk):
            continue
        cleaned = strip_activity_passages(chunk)
        if cleaned and len(cleaned) >= 100:
            filtered.append(cleaned)
    return filtered


def prepare_summary_context(
    chunks: list[str],
    max_chars: int | None = None,
    subject: str | None = None,
) -> str:
    """Build one context string from ordered chapter/document chunks."""
    return prepare_quiz_context(
        chunks,
        max_chars=max_chars or settings.summary_max_context_chars,
        subject=subject,
    )


def sample_summary_windows(chunks: list[str], window_size: int = 8) -> list[list[str]]:
    """Split usable chunks into overlapping windows for map-reduce summarization."""
    usable = filter_summary_source_chunks(chunks)
    if not usable:
        usable = [strip_activity_passages(chunk) for chunk in chunks if chunk.strip()]
        usable = [chunk for chunk in usable if len(chunk) >= 100]

    if len(usable) <= window_size:
        return [usable] if usable else []

    windows: list[list[str]] = [usable]
    step = max(1, window_size // 2)
    for start in range(0, max(1, len(usable) - window_size + 1), step):
        window = usable[start : start + window_size]
        if len(window) >= 4:
            windows.append(window)
    windows.append(stratified_sample_chunks(usable, min(window_size, len(usable))))
    return windows
