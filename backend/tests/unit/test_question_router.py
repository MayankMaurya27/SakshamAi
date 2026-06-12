"""Unit tests for question routing."""

from config.constants import AnswerProfile
from ai.question_router import (
    is_broad_concept_question,
    resolve_answer_profile,
)


def test_broad_concept_question_detects_overview_questions():
    assert is_broad_concept_question("What was the French Revolution?")
    assert is_broad_concept_question("Explain the causes of the French Revolution")
    assert not is_broad_concept_question("What is force?")


def test_resolve_answer_profile_activity_is_strict():
    profile = resolve_answer_profile(
        "What is the aim of Activity 5.7?",
        activity_refs=["Activity 5.7"],
    )
    assert profile == AnswerProfile.STRICT


def test_resolve_answer_profile_figure_is_strict():
    profile = resolve_answer_profile(
        "Explain Fig. 1.2",
        content_refs=["Fig. 1.2"],
    )
    assert profile == AnswerProfile.STRICT


def test_resolve_answer_profile_general_history_is_guided():
    profile = resolve_answer_profile("What was the French Revolution?")
    assert profile == AnswerProfile.GUIDED


def test_resolve_answer_profile_bio_is_strict():
    profile = resolve_answer_profile("Who was Meghnad Saha?")
    assert profile == AnswerProfile.STRICT
