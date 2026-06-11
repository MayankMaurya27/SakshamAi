"""Token-based text chunking using word approximation."""

import logging
import re

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Approximate tokens per word for English/Hindi mixed educational text
TOKENS_PER_WORD = 1.3


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


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to a maximum approximate token count."""
    words = _words(text)
    max_words = int(max_tokens / TOKENS_PER_WORD)
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])
