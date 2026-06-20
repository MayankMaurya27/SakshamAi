"""Unit tests for prompt builder."""

from config.constants import LearningMode
from ai.prompt_builder import (
    FALLBACK_RESPONSE,
    GLOBAL_SYSTEM_PROMPT,
    GUIDED_SYSTEM_PROMPT,
    STRICT_SYSTEM_PROMPT,
    build_fallback_prompt,
    build_prompt,
    build_quiz_prompt,
    format_retrieved_chunks,
)
from config.constants import AnswerProfile


def test_build_prompt_learn_mode_guided():
    """Guided learn mode should allow complete teacher-style answers."""
    prompt = build_prompt(
        LearningMode.LEARN,
        retrieved_context="Force is a push or pull.",
        question="What is force?",
        answer_profile=AnswerProfile.GUIDED,
    )
    assert "Use ONLY facts supported by the provided chapter context" in prompt
    assert "Force is a push or pull." in prompt
    assert "What is force?" in prompt


def test_build_prompt_learn_mode_strict():
    """Strict learn mode should stay context-only."""
    prompt = build_prompt(
        LearningMode.LEARN,
        retrieved_context="Force is a push or pull.",
        question="What is force?",
        answer_profile=AnswerProfile.STRICT,
    )
    assert STRICT_SYSTEM_PROMPT in prompt
    assert "Use ONLY the provided context" in prompt


def test_build_prompt_broad_question_addendum():
    """Broad questions should get structured answer guidance."""
    prompt = build_prompt(
        LearningMode.LEARN,
        retrieved_context="The French Revolution began in 1789.",
        question="What was the French Revolution?",
        answer_profile=AnswerProfile.GUIDED,
        broad_question=True,
    )
    assert "background or causes" in prompt


def test_build_prompt_all_modes():
    """All learning modes should produce non-empty prompts."""
    modes = [
        LearningMode.LEARN,
        LearningMode.SIMPLIFY,
        LearningMode.HINDI,
        LearningMode.QUIZ,
        LearningMode.SUMMARY,
        LearningMode.BEGINNER,
        LearningMode.DYSLEXIA,
        LearningMode.VISUAL,
        LearningMode.LEARN_FROM_SAKSHAM,
        LearningMode.KEY_CONCEPTS,
        LearningMode.AUTO_ANALYSIS,
    ]
    for mode in modes:
        prompt = build_prompt(
            mode,
            retrieved_context="context",
            question="question",
            document_text="document",
            topic="Force",
            grade=8,
        )
        assert len(prompt) > 50
        assert "Saksham AI" in prompt


def test_build_fallback_prompt():
    """Fallback should return standard message."""
    assert build_fallback_prompt() == FALLBACK_RESPONSE


def test_format_retrieved_chunks():
    """Chunks should be joined with separator."""
    result = format_retrieved_chunks(["chunk one", "chunk two"])
    assert "chunk one" in result
    assert "chunk two" in result
    assert "---" in result


def test_format_retrieved_chunks_empty():
    """Empty chunks should return empty string."""
    assert format_retrieved_chunks([]) == ""


def test_build_prompt_saksham_includes_question():
    """Saksham mode should answer directly without forced activity headings."""
    prompt = build_prompt(
        LearningMode.LEARN_FROM_SAKSHAM,
        retrieved_context="Communicable diseases spread through air and contact.",
        question="How are communicable diseases caused and spread?",
        topic="Health: The Ultimate Treasure",
        grade=8,
        answer_profile=AnswerProfile.GUIDED,
    )
    assert "How are communicable diseases caused and spread?" in prompt
    assert "Use ONLY facts supported by the provided chapter context" in prompt
    assert "Do not use Aim, Procedure, Observation" in prompt


def test_build_quiz_prompt_includes_question_count():
    """Quiz prompt should request the configured number of MCQs."""
    prompt = build_quiz_prompt(
        retrieved_context="Agriculture provides food and raw materials.",
        question_count=8,
        topic="Agriculture",
        grade=10,
    )
    assert "Generate exactly 8 multiple-choice questions" in prompt
    assert "valid JSON" in prompt
    assert "Agriculture provides food" in prompt


def test_global_system_prompt_alias():
    """GLOBAL_SYSTEM_PROMPT should remain available for older imports."""
    assert GLOBAL_SYSTEM_PROMPT == GUIDED_SYSTEM_PROMPT
