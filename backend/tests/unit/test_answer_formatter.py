"""Unit tests for answer and context formatting."""

from ai.answer_formatter import format_student_answer
from ai.context_cleaner import clean_context_text


def test_format_student_answer_strips_greeting():
    """Chatbot greetings and closings should be removed."""
    raw = (
        "Welcome to our lesson on Light!\n\n"
        "A mirror reflects light.\n\n"
        "Do you have any questions?"
    )
    result = format_student_answer(raw)
    assert "Welcome" not in result
    assert "Do you have any questions" not in result
    assert "mirror reflects light" in result


def test_format_student_answer_strips_meta_commentary():
    """Meta phrases about the student or context should be removed."""
    raw = (
        "You are right to ask about Activity 6.1. According to the context, "
        "pressure depends on height."
    )
    result = format_student_answer(raw)
    assert "You are right" not in result
    assert "According to the context" not in result
    assert "pressure depends on height" in result


def test_clean_context_text_normalizes_pdf_bullets():
    """PDF bullet markers should become readable list items."""
    raw = "Activity 6.1: Let us try z Take two pipes z Fill with water"
    result = clean_context_text(raw)
    assert "\n- Take two pipes" in result
    assert "\n- Fill with water" in result
