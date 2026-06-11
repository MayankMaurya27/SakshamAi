"""Unit tests for prompt builder."""

from config.constants import LearningMode
from ai.prompt_builder import (
    FALLBACK_RESPONSE,
    GLOBAL_SYSTEM_PROMPT,
    build_fallback_prompt,
    build_prompt,
    format_retrieved_chunks,
)


def test_build_prompt_learn_mode():
    """Learn mode prompt should include context and question."""
    prompt = build_prompt(
        LearningMode.LEARN,
        retrieved_context="Force is a push or pull.",
        question="What is force?",
    )
    assert GLOBAL_SYSTEM_PROMPT in prompt
    assert "Force is a push or pull." in prompt
    assert "What is force?" in prompt
    assert "Answer the question directly" in prompt


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
        assert GLOBAL_SYSTEM_PROMPT in prompt


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
    )
    assert "How are communicable diseases caused and spread?" in prompt
    assert "directly and comprehensively" in prompt
    assert "Do not use Aim, Procedure, Observation" in prompt
