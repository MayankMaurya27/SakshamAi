"""Clean PDF-extracted text before sending to the LLM."""

import re

_REPRINT_TAG = re.compile(r"Reprint\s+\d{4}-\d{2}", re.I)
_DOT_LEADERS = re.compile(r"\.{6,}")
_MULTI_SPACE = re.compile(r"[ \t]{2,}")
_BULLET_Z = re.compile(r"\s+z\s+")
_SPACED_LETTERS = re.compile(r"(?:\b[A-Za-z]\s){5,}[A-Za-z]\b")
_EXERCISE_START = re.compile(
    r"\b(?:Activities|Questions)\s*\??\s*\d+\.|\bBox\s+\d+\s+Activities\b",
    re.I,
)


def clean_context_text(text: str) -> str:
    """Normalize textbook chunk text for clearer LLM reading."""
    if not text:
        return text

    cleaned = _REPRINT_TAG.sub("", text)
    cleaned = _DOT_LEADERS.sub(" ", cleaned)
    cleaned = _BULLET_Z.sub("\n- ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = _MULTI_SPACE.sub(" ", cleaned)
    return cleaned.strip()


def clean_context_for_llm(text: str) -> str:
    """Trim textbook noise before sending context to the LLM."""
    cleaned = clean_context_text(text)
    if not cleaned:
        return cleaned

    match = _EXERCISE_START.search(cleaned)
    if match:
        cleaned = cleaned[: match.start()].strip()

    cleaned = _SPACED_LETTERS.sub(" ", cleaned)
    cleaned = re.sub(r"(?:Chapter\s+[IVXLC\d]+[^\n]{0,40}\n){2,}", "\n", cleaned, flags=re.I)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def trim_context_chunks(chunks: list[str], max_chars: int) -> list[str]:
    """Keep the most relevant chunks within a character budget for the LLM."""
    trimmed: list[str] = []
    total = 0
    for chunk in chunks:
        if not chunk:
            continue
        if total + len(chunk) <= max_chars:
            trimmed.append(chunk)
            total += len(chunk)
            continue
        remaining = max_chars - total
        if remaining < 250:
            break
        snippet = chunk[:remaining].rsplit(" ", 1)[0].strip()
        if snippet:
            trimmed.append(snippet + "...")
        break
    return trimmed
