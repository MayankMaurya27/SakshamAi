"""Deterministic summary helpers (offline, no LLM)."""

from __future__ import annotations

import re
from typing import Any

from services.quiz_grounded import (
    _ALSO_KNOWN_AS,
    _ARE_CALLED,
    _IS_CALLED,
    _IS_KNOWN_AS,
    _clean_phrase,
    _collect_definition_terms,
    _is_usable_definition,
    _normalize_term,
    _normalize_text,
)
from services.summary_parser import clean_summary_text, dedupe_sentences

_SECTION_TITLE = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s+([A-Z][A-Za-z0-9 \-]{4,80})\s*$",
    re.M,
)


def extract_section_titles(chunks: list[str]) -> list[str]:
    """Collect NCERT-style section headings from chapter chunks."""
    corpus = "\n".join(chunks)
    titles: list[str] = []
    seen: set[str] = set()
    for match in _SECTION_TITLE.finditer(corpus):
        title = _clean_phrase(match.group(2))
        key = title.lower()
        if key in seen or len(title) < 4:
            continue
        if re.search(r"\b(activity|exercise|questions)\b", title, re.I):
            continue
        seen.add(key)
        titles.append(title)
    return titles[:8]


def collect_definition_concepts(corpus: str) -> list[dict[str, str]]:
    """Extract grounded concept name/description pairs from chapter text."""
    concepts: list[dict[str, str]] = []
    seen: set[str] = set()

    for pattern in (_IS_CALLED, _ARE_CALLED, _IS_KNOWN_AS):
        for match in pattern.finditer(corpus):
            subject = _clean_phrase(match.group(1))
            term = _normalize_term(_clean_phrase(match.group(2)))
            if not _is_usable_definition(subject, term):
                continue
            key = term.lower()
            if key in seen:
                continue
            seen.add(key)
            concepts.append(
                {
                    "name": term,
                    "description": _normalize_text(match.group(0))[:200],
                }
            )

    for match in _ALSO_KNOWN_AS.finditer(corpus):
        primary = _clean_phrase(match.group(1))
        for idx in (1, 2):
            term = _normalize_term(_clean_phrase(match.group(idx)))
            key = term.lower()
            if key in seen:
                continue
            if not _is_usable_definition(primary, term):
                continue
            seen.add(key)
            concepts.append(
                {
                    "name": term,
                    "description": _normalize_text(match.group(0))[:200],
                }
            )

    return concepts[:10]


def build_fallback_summary(
    chunks: list[str],
    chapter_title: str = "",
) -> dict[str, Any]:
    """Build a minimal grounded summary when the LLM output is unusable."""
    corpus = "\n".join(chunks)
    concepts = collect_definition_concepts(corpus)
    if not concepts:
        terms = _collect_definition_terms(corpus)
        concepts = [{"name": term, "description": term} for term in terms[:6]]

    paragraphs: list[str] = []
    if concepts:
        for start in range(0, min(len(concepts), 6), 2):
            group = concepts[start : start + 2]
            paragraph = dedupe_sentences(
                " ".join(item["description"] for item in group),
                max_chars=500,
            )
            if paragraph:
                paragraphs.append(paragraph)
    else:
        label = chapter_title or "this chapter"
        paragraphs.append(
            f"This summary covers the main ideas from {label} based on the source text."
        )

    summary = clean_summary_text("\n\n".join(paragraphs))
    return {
        "summary": summary,
        "format_version": "v2-prose-fallback",
    }
