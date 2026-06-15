"""Deterministic answers for textbook biography and sidebar profiles."""

import re

_PROFILE_HEADERS = (
    "be a scientist",
    "ever heard of",
    "our scientific heritage",
    "do you know",
)

_BIO_QUESTION_PATTERN = re.compile(
    r"\bwho\s+(?:was|is|were|are)\b",
    re.I,
)

_PASSAGE_STOP_PATTERNS = [
    re.compile(r"(?<=\.)\s+\d+\.\d+\s"),
    re.compile(r"\bActivity\s+\d", re.I),
    re.compile(r"\bFig\.\s+\d", re.I),
    re.compile(r"Reprint\s+20", re.I),
    re.compile(r"\bA step further\b", re.I),
]


def _profile_start(text_lower: str, name_pos: int) -> int:
    """Pick the sidebar header closest before the person's name."""
    best = name_pos
    best_distance = float("inf")
    for header in _PROFILE_HEADERS:
        hpos = text_lower.rfind(header, max(0, name_pos - 700), name_pos + 40)
        if hpos < 0:
            continue
        distance = name_pos - hpos
        if distance < best_distance:
            best_distance = distance
            best = hpos
    return best


_CONCEPT_HINTS = (
    "revolution",
    "war",
    "movement",
    "empire",
    "dynasty",
    "independence",
    "democracy",
    "constitution",
    "economy",
    "development",
    "government",
    "rebellion",
    "colonialism",
    "nationalism",
)


def is_bio_question(question: str) -> bool:
    """Return True when the student is asking about a person, not an event or concept."""
    if not _BIO_QUESTION_PATTERN.search(question):
        return False
    q = question.lower()
    if any(hint in q for hint in _CONCEPT_HINTS):
        return False
    return True


def try_format_bio_answer(context_text: str, query_terms: list[str]) -> str | None:
    """
    Extract a biography sidebar (e.g. 'Be a scientist') when the context contains it.

    Returns a cleaned paragraph suitable for direct display, or None.
    """
    if not context_text or not query_terms:
        return None

    text = context_text
    text_lower = text.lower()

    for term in sorted(query_terms, key=len, reverse=True):
        if len(term) < 4:
            continue
        name_pos = text_lower.find(term.lower())
        if name_pos < 0:
            continue

        start = _profile_start(text_lower, name_pos)
        if start >= name_pos:
            # No sidebar header (e.g. "Be a scientist") before the term — not a bio block.
            continue

        end = len(text)
        for pattern in _PASSAGE_STOP_PATTERNS:
            match = pattern.search(text, name_pos + len(term))
            if match and match.start() < end:
                end = match.start()

        passage = text[start:end].strip()
        if len(passage) < 50 or term.lower() not in passage.lower():
            continue

        for header in _PROFILE_HEADERS:
            passage = re.sub(
                rf"^{re.escape(header)}\s*",
                "",
                passage,
                count=1,
                flags=re.I,
            )

        passage = re.sub(r"\s+", " ", passage).strip()
        return passage

    return None
