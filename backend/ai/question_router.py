"""Route student questions to strict or guided answer generation."""

import re

from ai.bio_formatter import is_bio_question
from config.constants import AnswerProfile

_BROAD_QUESTION_PATTERN = re.compile(
    r"\b(?:"
    r"what\s+(?:was|were)\b|"
    r"explain\b|"
    r"describe\b|"
    r"tell\s+me\s+about\b|"
    r"give\s+(?:an\s+)?overview\b|"
    r"significance\s+of\b|"
    r"importance\s+of\b|"
    r"legacy\s+of\b|"
    r"causes?\s+of\b|"
    r"why\s+did\b|"
    r"how\s+did\b|"
    r"summari[sz]e\b|"
    r"introduction\s+to\b"
    r")\b",
    re.I,
)


def is_broad_concept_question(question: str) -> bool:
    """Return True for chapter-level or overview questions needing structured answers."""
    text = question.strip()
    if not text:
        return False
    return bool(_BROAD_QUESTION_PATTERN.search(text))


def resolve_answer_profile(
    question: str,
    activity_refs: list[str] | None = None,
    content_refs: list[str] | None = None,
) -> AnswerProfile:
    """
    Choose strict textbook grounding or guided teaching for LLM generation.

    Activities, figures, exercises, and biography questions stay strict.
    General chapter questions use guided mode so the model can explain completely
    while staying aligned with NCERT-level facts.
    """
    if content_refs is None:
        from ai.retriever import extract_content_refs

        refs = extract_content_refs(question)
    else:
        refs = content_refs

    acts = activity_refs if activity_refs is not None else [
        ref for ref in refs if ref.lower().startswith("activity")
    ]

    if acts:
        return AnswerProfile.STRICT
    if any(ref.lower().startswith(("fig", "exercise")) for ref in refs):
        return AnswerProfile.STRICT
    if is_bio_question(question):
        return AnswerProfile.STRICT

    return AnswerProfile.GUIDED


def context_char_limit(profile: AnswerProfile, settings) -> int:
    """Return the context budget for the given answer profile."""
    if profile == AnswerProfile.GUIDED:
        return settings.max_llm_context_chars_guided
    return settings.max_llm_context_chars


def retrieval_top_k(profile: AnswerProfile, settings) -> int:
    """Return how many chunks to retrieve for the given answer profile."""
    if profile == AnswerProfile.GUIDED:
        return settings.top_k_guided
    return settings.top_k
