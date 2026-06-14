"""Clean and merge plain-text summary responses from the local LLM."""

from __future__ import annotations

import re

_SECTION_HEADERS = (
    "OVERVIEW",
    "KEY CONCEPTS",
    "SECTION NOTES",
    "REVISION POINTS",
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _normalize_sentence_key(sentence: str) -> str:
    normalized = re.sub(r"\s+", " ", sentence.lower().strip())
    return re.sub(r"[^\w\s]", "", normalized)


def _word_overlap(left: str, right: str) -> float:
    words_left = set(_normalize_sentence_key(left).split())
    words_right = set(_normalize_sentence_key(right).split())
    if not words_left or not words_right:
        return 0.0
    return len(words_left & words_right) / len(words_left | words_right)


def _same_opening(left: str, right: str, word_count: int = 6) -> bool:
    left_words = _normalize_sentence_key(left).split()
    right_words = _normalize_sentence_key(right).split()
    if len(left_words) < word_count or len(right_words) < word_count:
        return False
    return left_words[:word_count] == right_words[:word_count]


def dedupe_sentences(text: str, max_chars: int = 800) -> str:
    """Drop repeated or near-duplicate sentences from summary prose."""
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return ""

    kept: list[str] = []
    for sentence in _SENTENCE_SPLIT.split(cleaned):
        candidate = sentence.strip()
        if len(candidate) < 12:
            continue
        candidate_key = _normalize_sentence_key(candidate)
        is_duplicate = False
        for existing in kept:
            existing_key = _normalize_sentence_key(existing)
            if candidate_key == existing_key:
                is_duplicate = True
                break
            if candidate_key in existing_key or existing_key in candidate_key:
                is_duplicate = True
                break
            if _same_opening(candidate, existing):
                is_duplicate = True
                break
            if _word_overlap(candidate, existing) >= 0.68:
                is_duplicate = True
                break
        if not is_duplicate:
            kept.append(candidate)

    merged = " ".join(kept).strip()
    if len(merged) <= max_chars:
        return merged
    truncated = merged[:max_chars].rsplit(" ", 1)[0]
    return truncated.strip() or merged[:max_chars].strip()


def count_paragraphs(text: str) -> int:
    return len([part for part in re.split(r"\n\s*\n", text.strip()) if part.strip()])


def count_words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def strip_legacy_section_headers(text: str) -> str:
    """Convert old sectioned LLM output into plain paragraphs."""
    pattern = r"(?mi)^(" + "|".join(re.escape(header) for header in _SECTION_HEADERS) + r")\s*$"
    parts = re.split(pattern, text.strip())
    if len(parts) <= 1:
        return text.strip()

    bodies: list[str] = []
    idx = 1
    while idx + 1 < len(parts):
        body = parts[idx + 1].strip()
        if body:
            bodies.append(body)
        idx += 2
    return "\n\n".join(bodies).strip() if bodies else text.strip()


def _split_long_block_into_paragraphs(text: str, sentences_per_para: int = 2) -> str:
    sentences = [
        sentence.strip()
        for sentence in _SENTENCE_SPLIT.split(text)
        if len(sentence.strip()) >= 12
    ]
    if len(sentences) < 2:
        return text.strip()

    paragraphs: list[str] = []
    for start in range(0, len(sentences), sentences_per_para):
        paragraph = " ".join(sentences[start : start + sentences_per_para]).strip()
        if paragraph:
            paragraphs.append(paragraph)
    return "\n\n".join(paragraphs)


def _dedupe_paragraphs(paragraphs: list[str], paragraph_max_chars: int = 1200) -> list[str]:
    kept: list[str] = []
    seen: set[str] = set()
    for paragraph in paragraphs:
        cleaned = dedupe_sentences(paragraph.strip(), max_chars=paragraph_max_chars)
        if len(cleaned) < 30:
            continue
        key = _normalize_sentence_key(cleaned)[:120]
        if key in seen:
            continue
        if any(_word_overlap(cleaned, existing) >= 0.68 for existing in kept):
            continue
        seen.add(key)
        kept.append(cleaned)
    return kept


def _truncate_preserving_paragraphs(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text.strip()

    kept: list[str] = []
    total = 0
    for paragraph in text.split("\n\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        extra = len(paragraph) + (2 if kept else 0)
        if total + extra > max_chars:
            break
        kept.append(paragraph)
        total += extra
    return "\n\n".join(kept).strip() or text[:max_chars].strip()


def clean_summary_text(text: str, max_chars: int | None = None) -> str:
    """Normalize LLM output into readable multi-paragraph prose."""
    if max_chars is None:
        from config.settings import get_settings

        max_chars = get_settings().summary_max_chars
    cleaned = strip_legacy_section_headers(text.strip())
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"^\s*[-•*]\s+", "", cleaned, flags=re.M)

    if count_paragraphs(cleaned) < 2 and len(cleaned) > 80:
        cleaned = _split_long_block_into_paragraphs(cleaned)

    paragraphs = _dedupe_paragraphs(
        [part.strip() for part in re.split(r"\n\s*\n", cleaned) if part.strip()]
    )
    result = "\n\n".join(paragraphs).strip()
    return _truncate_preserving_paragraphs(result, max_chars)


def merge_partial_summaries(texts: list[str], max_chars: int | None = None) -> str:
    """Merge window summaries without repeating similar paragraphs."""
    if max_chars is None:
        from config.settings import get_settings

        max_chars = get_settings().summary_max_chars
    paragraphs: list[str] = []
    for text in texts:
        cleaned = clean_summary_text(text, max_chars=max_chars)
        paragraphs.extend(part for part in cleaned.split("\n\n") if part.strip())
    merged = "\n\n".join(_dedupe_paragraphs(paragraphs)).strip()
    return _truncate_preserving_paragraphs(merged, max_chars)
