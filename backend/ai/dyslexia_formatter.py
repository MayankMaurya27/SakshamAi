"""Deterministic dyslexia-friendly text formatting (no LLM)."""

from __future__ import annotations

import re
from typing import Iterable

from config.settings import get_settings

settings = get_settings()

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_BULLET_LINE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")
_CONNECTOR = re.compile(
    r"\b(?:furthermore|consequently|in addition|moreover|nevertheless|"
    r"therefore|however|additionally|on the other hand)\b,?\s*",
    re.I,
)
_SPLIT_CONJUNCTION = re.compile(
    r"\b(?:,\s*(?:and|but|or|so|because|which|who|when|where|while|although)\s+|"
    r"\s+(?:and|but|or|so|because|which|who|when|where|while|although)\s+)",
    re.I,
)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _strip_connectors(text: str) -> str:
    cleaned = _CONNECTOR.sub("", text)
    return re.sub(r"\s{2,}", " ", cleaned).strip()


def _split_long_sentence(sentence: str, max_words: int) -> list[str]:
    stripped = sentence.strip()
    if not stripped or _word_count(stripped) <= max_words:
        return [stripped] if stripped else []

    parts: list[str] = []
    for match in _SPLIT_CONJUNCTION.finditer(stripped):
        prefix = stripped[: match.start()].strip(" ,;")
        if prefix and _word_count(prefix) >= 4:
            parts.append(prefix)
            stripped = stripped[match.end() :].strip()
    if stripped:
        parts.append(stripped.strip(" ,;."))

    if len(parts) <= 1 and _word_count(stripped) > max_words:
        words = stripped.split()
        chunk: list[str] = []
        for word in words:
            chunk.append(word)
            if len(chunk) >= max_words:
                parts.append(" ".join(chunk))
                chunk = []
        if chunk:
            parts.append(" ".join(chunk))
        return [part.strip(" ,;.") for part in parts if part.strip()]

    refined: list[str] = []
    for part in parts:
        refined.extend(_split_long_sentence(part, max_words))
    return refined


def _split_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    for block in re.split(r"\n\s*\n", text.strip()):
        block = block.strip()
        if not block:
            continue
        for line in block.splitlines():
            line = line.strip()
            if not line:
                continue
            if _BULLET_LINE.match(line):
                sentences.append(_BULLET_LINE.sub("", line).strip())
                continue
            for sentence in _SENTENCE_SPLIT.split(line):
                stripped = sentence.strip()
                if stripped:
                    sentences.append(stripped)
    return sentences


def _chunk_bullets(bullets: list[str], block_size: int) -> list[str]:
    if not bullets:
        return []
    blocks: list[str] = []
    for start in range(0, len(bullets), block_size):
        chunk = bullets[start : start + block_size]
        blocks.append("\n".join(f"• {item}" for item in chunk))
    return blocks


def extract_preserve_terms(corpus: str, min_len: int = 5) -> set[str]:
    """Collect longer textbook terms from source text for preservation."""
    terms: set[str] = set()
    for match in re.finditer(r"\b[A-Za-z][A-Za-z\-]{4,}\b", corpus):
        terms.add(match.group(0))
    return {term for term in terms if len(term) >= min_len}


def split_reading_segments(formatted_text: str) -> list[str]:
    """Return bullet/sentence segments for read-along highlighting."""
    segments: list[str] = []
    for block in formatted_text.split("\n\n"):
        for line in block.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("•"):
                segments.append(line.lstrip("•").strip())
            elif re.match(r"^\d+[.)]\s+", line):
                segments.append(re.sub(r"^\d+[.)]\s+", "", line).strip())
            else:
                segments.extend(part.strip() for part in _SENTENCE_SPLIT.split(line) if part.strip())
    return segments


_BRACKET_DEF = re.compile(r"\s*\[([^\]]+)\]")


def prepare_segment_for_speech(segment: str) -> str:
    """Convert one reading segment into natural spoken text."""
    spoken = segment.strip()
    if not spoken:
        return ""
    spoken = _BRACKET_DEF.sub(r". \1", spoken)
    spoken = re.sub(r"\s{2,}", " ", spoken).strip(" .")
    return spoken


def build_pointwise_speech_lines(segments: list[str]) -> list[str]:
    """Build one spoken utterance per visible bullet or numbered point."""
    lines: list[str] = []
    for index, segment in enumerate(segments, start=1):
        body = prepare_segment_for_speech(segment)
        if not body:
            continue
        lines.append(f"Point {index}. {body}.")
    return lines


def extract_speech_points(text: str) -> list[str]:
    """Split formatted or raw text into discrete speech points when list-like."""
    if not text or not text.strip():
        return []

    has_bullets = "•" in text or bool(re.search(r"(?m)^\s*[-*]\s+", text))
    has_numbered = bool(re.search(r"(?m)^\s*\d+[.)]\s+", text))

    if has_bullets:
        segments = split_reading_segments(text)
        if segments:
            return segments

    if has_numbered:
        numbered: list[str] = []
        for line in text.splitlines():
            line = line.strip()
            match = re.match(r"^\d+[.)]\s+(.*)$", line)
            if match:
                numbered.append(match.group(1).strip())
        if numbered:
            return numbered

    return [text.strip()]


def format_dyslexia_text(
    text: str,
    preserve_terms: Iterable[str] | None = None,
    max_words_per_sentence: int | None = None,
    max_bullets: int | None = None,
    bullets_per_block: int = 3,
) -> str:
    """Format text into short bullet blocks for dyslexia-friendly reading."""
    if not text or not text.strip():
        return text

    max_words = max_words_per_sentence or settings.dyslexia_max_words_per_sentence
    bullet_cap = max_bullets or settings.dyslexia_max_bullets

    sentences = _split_sentences(text)
    short_sentences: list[str] = []
    for sentence in sentences:
        cleaned = _strip_connectors(sentence)
        if not cleaned:
            continue
        short_sentences.extend(_split_long_sentence(cleaned, max_words))

    bullets: list[str] = []
    seen: set[str] = set()
    for sentence in short_sentences:
        normalized = sentence.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        bullets.append(sentence.rstrip("."))
        if len(bullets) >= bullet_cap:
            break

    if not bullets:
        return text.strip()

    return "\n\n".join(_chunk_bullets(bullets, bullets_per_block))
