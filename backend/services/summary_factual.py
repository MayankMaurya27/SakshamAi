"""Strip textbook narratives and keep summary sentences grounded in source text."""

from __future__ import annotations

import re

from services.quiz_grounded import _normalize_text, _text_in_corpus

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

_NARRATIVE_MARKERS = re.compile(
    r"\b(?:"
    r"Bhavisha|Dhruv|Itih[aā]sa|time machine|"
    r"Ira,?\s+daughter of Kanhadas|Kanhadas|"
    r"introduced herself|activated their|whisked away|"
    r"Landing on the outskirts|Glad to meet you|Keep your voices down|"
    r"Jonali|Pallabi|Arshad|Ajay|"
    r"Exploring Society: India and Beyond|Tapestry of the Past"
    r")\b",
    re.I,
)

_DIALOGUE_LINE = re.compile(
    r"(?:^|[\n\r])\s*(?:"
    r"[“\"'].|[“\"']$|"
    r"(?:Bhavisha|Dhruv|Ira|Tour Guide)\s*:|"
    r"(?:asked|remarked|explained|answered|wondered)\s+(?:Bhavisha|Dhruv|Ira|they)"
    r")",
    re.I,
)

_STORY_ACTION = re.compile(
    r"\b(?:"
    r"they decided to visit|they saw a girl|cross the same drawbridge|"
    r"Let's join Bhavisha|journey to the|itching for another adventure|"
    r"could not wait to find out"
    r")\b",
    re.I,
)

_FACTUAL_ANCHOR = re.compile(
    r"(?:"
    r"What is an Empire\?|Features of an empire|Tributary:|"
    r"Indian history is full of empires|"
    r"Maintains an army to keep|Simply put, an empire is|"
    r"In ancient Sanskrit texts, words commonly used"
    r")",
    re.I,
)

_STOPWORDS = frozenset(
    {
        "about", "after", "also", "been", "from", "into", "more", "other",
        "over", "such", "than", "that", "their", "them", "these", "they",
        "this", "through", "under", "very", "were", "which", "while", "with",
        "would", "there", "where", "when", "what", "many", "some", "only",
    }
)


def is_narrative_sentence(sentence: str) -> bool:
    stripped = sentence.strip()
    if not stripped or len(stripped) < 12:
        return True
    if _NARRATIVE_MARKERS.search(stripped):
        return True
    if _DIALOGUE_LINE.search(stripped):
        return True
    if _STORY_ACTION.search(stripped):
        return True
    if stripped.count('"') >= 2 or stripped.count("\u201c") >= 1:
        return True
    return False


def strip_narrative_sentences(text: str) -> str:
    """Remove story framing and dialogue; keep factual textbook sentences."""
    if not text.strip():
        return ""

    anchor = _FACTUAL_ANCHOR.search(text)
    segments: list[str] = []
    if anchor:
        segments.append(text[anchor.start() :])

    kept: list[str] = []
    for segment in segments or [text]:
        for sentence in _SENTENCE_SPLIT.split(segment):
            stripped = sentence.strip()
            if not stripped or is_narrative_sentence(stripped):
                continue
            kept.append(stripped)

    if not kept:
        for sentence in _SENTENCE_SPLIT.split(text):
            stripped = sentence.strip()
            if not stripped or is_narrative_sentence(stripped):
                continue
            kept.append(stripped)

    return " ".join(kept).strip()


def is_narrative_heavy_chunk(text: str) -> bool:
    cleaned = text.strip()
    if not cleaned:
        return True
    sentences = [part.strip() for part in _SENTENCE_SPLIT.split(cleaned) if part.strip()]
    if not sentences:
        return True
    narrative_hits = sum(1 for sentence in sentences if is_narrative_sentence(sentence))
    return narrative_hits >= max(2, len(sentences) // 2)


def _has_phrase_overlap(sentence: str, corpus: str, size: int = 4) -> bool:
    words = re.findall(r"[a-z]+", sentence.lower())
    if len(words) < size:
        return False
    lowered = corpus.lower()
    for start in range(len(words) - size + 1):
        phrase = " ".join(words[start : start + size])
        if phrase in lowered:
            return True
    return False


def is_summary_sentence_grounded(sentence: str, corpus: str) -> bool:
    stripped = sentence.strip()
    if len(stripped) < 20:
        return False
    if is_narrative_sentence(stripped):
        return False

    normalized = _normalize_text(stripped)
    corpus_norm = _normalize_text(corpus)
    if _text_in_corpus(normalized, corpus_norm):
        return True
    if _has_phrase_overlap(stripped, corpus_norm, size=4):
        return True

    tokens = [
        token
        for token in re.findall(r"[a-z]{5,}", normalized.lower())
        if token not in _STOPWORDS
    ]
    if len(tokens) < 3:
        return False
    hits = sum(1 for token in tokens if token in corpus_norm.lower())
    return hits >= max(3, int(len(tokens) * 0.45))


def ground_summary_text(summary: str, corpus: str) -> str:
    """Keep only summary sentences supported by the source chapter text."""
    paragraphs: list[str] = []
    for paragraph in summary.split("\n\n"):
        kept: list[str] = []
        for sentence in _SENTENCE_SPLIT.split(paragraph.strip()):
            stripped = sentence.strip()
            if not stripped:
                continue
            if is_summary_sentence_grounded(stripped, corpus):
                kept.append(stripped)
        if kept:
            paragraphs.append(" ".join(kept))
    return "\n\n".join(paragraphs).strip()
