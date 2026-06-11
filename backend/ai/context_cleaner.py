"""Clean PDF-extracted text before sending to the LLM."""

import re

_REPRINT_TAG = re.compile(r"Reprint\s+\d{4}-\d{2}", re.I)
_DOT_LEADERS = re.compile(r"\.{6,}")
_MULTI_SPACE = re.compile(r"[ \t]{2,}")
_BULLET_Z = re.compile(r"\s+z\s+")


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
