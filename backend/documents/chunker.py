"""Token-based text chunking using word approximation."""

import logging
import re

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Approximate tokens per word for English/Hindi mixed educational text
TOKENS_PER_WORD = 1.3

# NCERT-style section boundaries for curriculum-aware chunking
_SECTION_BREAK = re.compile(
    r"(?="
    r"\d+\.\d+\s+[A-Z\u0900-\u097F]"  # 1.4 Modern Farming
    r"|\d+\.\s+[A-Z\u0900-\u097F]"  # 5. Who will provide
    r"|Let's Discuss"
    r"|Let\u2019s Discuss"
    r"|Suggested Activity"
    r"|Exercises\b"
    r"|Summary\b"
    r"|Overview\b"
    r")",
    re.I,
)

_MIN_SECTION_CHARS = 120
_SECTION_START = re.compile(r"^\d+\.(\d+)?\s+", re.I)


def _words(text: str) -> list[str]:
    """Split text into words."""
    return re.findall(r"\S+", text)


def _count_tokens(text: str) -> int:
    """Approximate token count from word count."""
    return int(len(_words(text)) * TOKENS_PER_WORD)


def create_chunks(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    """
    Split text into overlapping token-based chunks.

    Uses word-count approximation (1.3 tokens per word) compatible with
    edge deployment without tiktoken dependency.

    Args:
        text: Input text to chunk.
        chunk_size: Maximum tokens per chunk (default from settings).
        overlap: Token overlap between chunks (default from settings).

    Returns:
        List of text chunks.
    """
    chunk_size = chunk_size or settings.chunk_size_tokens
    overlap = overlap or settings.chunk_overlap_tokens

    if overlap >= chunk_size:
        overlap = chunk_size // 4

    words = _words(text)
    if not words:
        return []

    words_per_chunk = max(1, int(chunk_size / TOKENS_PER_WORD))
    words_overlap = max(1, int(overlap / TOKENS_PER_WORD))

    chunks: list[str] = []
    start = 0

    while start < len(words):
        end = min(start + words_per_chunk, len(words))
        chunk_text = " ".join(words[start:end]).strip()
        if chunk_text:
            chunks.append(chunk_text)
        if end >= len(words):
            break
        start += words_per_chunk - words_overlap

    logger.info(
        "Created %d chunks from ~%d tokens",
        len(chunks),
        _count_tokens(text),
    )
    return chunks


def _split_curriculum_sections(text: str) -> list[str]:
    """Split textbook text on section-like boundaries before token chunking."""
    parts = [part.strip() for part in _SECTION_BREAK.split(text) if part.strip()]
    if not parts:
        stripped = text.strip()
        return [stripped] if stripped else []

    sections: list[str] = []
    for part in parts:
        is_section_start = bool(_SECTION_START.match(part))
        if not sections:
            sections.append(part)
            continue
        if is_section_start or len(part) >= _MIN_SECTION_CHARS:
            sections.append(part)
            continue
        sections[-1] = f"{sections[-1]} {part}".strip()

    return sections


def create_curriculum_chunks(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    """
    Chunk NCERT PDF text by section first, then by token size.

    Keeps related paragraphs together (e.g. farm labour wages vs irrigation)
    which improves hybrid retrieval accuracy.
    """
    chunk_size = chunk_size or settings.chunk_size_tokens
    overlap = overlap or settings.chunk_overlap_tokens

    sections = _split_curriculum_sections(text)
    if not sections:
        return create_chunks(text, chunk_size, overlap)

    chunks: list[str] = []
    for section in sections:
        if _count_tokens(section) <= chunk_size:
            chunks.append(section)
        else:
            chunks.extend(create_chunks(section, chunk_size, overlap))

    logger.info(
        "Created %d curriculum chunks from %d sections (~%d tokens)",
        len(chunks),
        len(sections),
        _count_tokens(text),
    )
    return chunks


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to a maximum approximate token count."""
    words = _words(text)
    max_words = int(max_tokens / TOKENS_PER_WORD)
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])
