"""Prepare chapter/document text for summary generation."""

from __future__ import annotations

import re

from ai.context_cleaner import clean_context_for_llm, clean_context_text
from config.settings import get_settings
from services.quiz_context import (
    is_exercise_list_chunk,
    prepare_quiz_context,
    stratified_sample_chunks,
)
from services.quiz_math import filter_math_quiz_chunks, is_math_subject

from services.summary_factual import strip_narrative_sentences

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
    """Drop exercises, activities, narratives, and low-quality chunks before summarization."""
    source = filter_math_quiz_chunks(chunks) if is_math_subject(subject) else chunks
    filtered: list[str] = []
    for chunk in source:
        if not chunk or not chunk.strip():
            continue
        if is_exercise_list_chunk(chunk):
            continue
        if is_activity_heavy_chunk(chunk):
            continue
        cleaned = strip_narrative_sentences(strip_activity_passages(chunk))
        if cleaned and len(cleaned) >= 60:
            filtered.append(clean_context_for_llm(clean_context_text(cleaned)))
    return filtered


def prepare_summary_context(
    chunks: list[str],
    max_chars: int | None = None,
    subject: str | None = None,
) -> str:
    """Build one context string from factual chapter/document chunks."""
    usable = filter_summary_source_chunks(chunks, subject=subject)
    source = usable if usable else chunks
    return prepare_quiz_context(
        source,
        max_chars=max_chars or settings.summary_max_context_chars,
        subject=subject,
    )


def sample_summary_windows(chunks: list[str], window_size: int = 8) -> list[list[str]]:
    """Split usable chunks into overlapping windows for map-reduce summarization."""
    usable = filter_summary_source_chunks(chunks)
    if not usable:
        usable = []
        for chunk in chunks:
            if not chunk.strip():
                continue
            cleaned = strip_narrative_sentences(strip_activity_passages(chunk))
            if cleaned and len(cleaned) >= 60:
                usable.append(clean_context_for_llm(clean_context_text(cleaned)))

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
