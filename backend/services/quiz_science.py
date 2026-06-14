"""Science quiz helpers — delegates to generic grounded generation."""

from __future__ import annotations

from typing import Any

from services.quiz_grounded import (
    build_grounded_chapter_questions,
    extract_definition_questions,
    filter_grounded_questions,
    is_valid_grounded_question,
)

_SCIENCE_SUBJECTS = frozenset({"science"})


def is_science_subject(subject: str | None) -> bool:
    """Return True for NCERT Science quizzes."""
    if not subject:
        return False
    return subject.strip().lower() in _SCIENCE_SUBJECTS


def extract_science_definition_questions(chunks: list[str], count: int) -> list[dict[str, Any]]:
    """Backward-compatible wrapper for definition extraction."""
    from services.quiz_grounded import _collect_phrase_pool

    return extract_definition_questions(chunks, count, set(), _collect_phrase_pool(chunks))


def build_science_concept_questions(
    chunks: list[str],
    count: int,
    chapter_title: str = "",
) -> list[dict[str, Any]]:
    """Build factual MCQs grounded in chapter text."""
    return build_grounded_chapter_questions(chunks, count, chapter_title=chapter_title)


def is_valid_science_question(question: str, options: dict[str, str]) -> bool:
    return is_valid_grounded_question(question, options)


def filter_science_questions(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only usable science MCQs."""
    return filter_grounded_questions(questions)
