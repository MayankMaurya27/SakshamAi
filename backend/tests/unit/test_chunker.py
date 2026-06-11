"""Unit tests for text chunking."""

from documents.chunker import create_chunks, truncate_to_tokens


def test_create_chunks_splits_long_text():
    """Long text should produce multiple chunks."""
    text = "word " * 2000
    chunks = create_chunks(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(chunk) > 0 for chunk in chunks)


def test_create_chunks_empty_text():
    """Empty text should return empty list."""
    assert create_chunks("") == []


def test_create_chunks_short_text():
    """Short text should produce single chunk."""
    text = "This is a short educational text about science."
    chunks = create_chunks(text, chunk_size=700, overlap=100)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_truncate_to_tokens():
    """Truncation should limit token count."""
    text = "word " * 500
    truncated = truncate_to_tokens(text, max_tokens=50)
    assert len(truncated) < len(text)
