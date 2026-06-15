"""Hindi text formatting helpers for localization output."""

from __future__ import annotations

import re

_DEVANAGARI = re.compile(r"[\u0900-\u097F]")
_BULLET_LINE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")
_LATIN_TERM = re.compile(r"\b[A-Za-z][A-Za-z0-9+\-]{2,}\b")


def devanagari_char_count(text: str) -> int:
    return len(_DEVANAGARI.findall(text))


def devanagari_ratio(text: str) -> float:
    """Return ratio of Devanagari chars to all non-whitespace chars."""
    stripped = re.sub(r"\s+", "", text)
    if not stripped:
        return 0.0
    return devanagari_char_count(text) / len(stripped)


def extract_preserve_terms_from_english(text: str, min_len: int = 4) -> list[str]:
    """Collect Latin tokens from English source text worth preserving in Hinenglish."""
    terms: list[str] = []
    seen: set[str] = set()
    for match in _LATIN_TERM.finditer(text):
        term = match.group(0)
        if len(term) < min_len:
            continue
        key = term.lower()
        if key in seen:
            continue
        seen.add(key)
        terms.append(term)
    return terms


def split_reading_segments(hindi_text: str) -> list[str]:
    """Split Hinenglish text into segments for read-along highlighting."""
    segments: list[str] = []
    for block in hindi_text.split("\n\n"):
        for line in block.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("•"):
                segments.append(line.lstrip("•").strip())
            elif _BULLET_LINE.match(line):
                segments.append(_BULLET_LINE.sub("", line).strip())
            else:
                parts = re.split(r"(?<=[।!?])\s+", line)
                segments.extend(part.strip() for part in parts if part.strip())
    return segments


def extract_speech_points(hindi_text: str) -> list[str]:
    """Extract discrete speech points from formatted Hinenglish text."""
    segments = split_reading_segments(hindi_text)
    if len(segments) > 1:
        return segments
    stripped = hindi_text.strip()
    return [stripped] if stripped else []


def prepare_segment_for_speech(segment: str) -> str:
    """Normalize one Hindi segment for TTS."""
    spoken = segment.strip()
    if not spoken:
        return ""
    spoken = spoken.replace("•", " ")
    spoken = re.sub(r"\s{2,}", " ", spoken).strip(" ।.")
    return spoken


def build_hindi_pointwise_speech_lines(segments: list[str]) -> list[str]:
    """Build one spoken utterance per bullet with Hindi point labels."""
    lines: list[str] = []
    for index, segment in enumerate(segments, start=1):
        body = prepare_segment_for_speech(segment)
        if not body:
            continue
        lines.append(f"बिंदु {index}. {body}.")
    return lines
