"""Unit tests for Hinenglish validation."""

from ai.hindi_validator import (
    parse_quiz_question_json,
    validate_prose_hindi,
    validate_quiz_payload,
    validate_quiz_question,
)


def test_validate_prose_hindi_accepts_devanagari():
    ok, reason = validate_prose_hindi(
        "• प्रकाश संश्लेषण (Photosynthesis) पौधों में होता है।"
    )
    assert ok is True
    assert reason == ""


def test_validate_prose_hindi_rejects_english_only():
    ok, reason = validate_prose_hindi("Photosynthesis is a process in plants.")
    assert ok is False
    assert "Devanagari" in reason


def test_parse_quiz_question_json():
    raw = (
        '{"question": "बल क्या है?", "option_a": "धक्का", "option_b": "रंग", '
        '"option_c": "ध्वनि", "option_d": "प्रकाश", "correct_answer": "A"}'
    )
    parsed = parse_quiz_question_json(raw)
    assert parsed is not None
    assert parsed["correct_answer"] == "A"


def test_validate_quiz_question_preserves_correct_answer():
    original = {
        "question": "What is force?",
        "option_a": "Push",
        "option_b": "Color",
        "option_c": "Sound",
        "option_d": "Light",
        "correct_answer": "B",
    }
    translated = {
        "question": "बल क्या है?",
        "option_a": "धक्का",
        "option_b": "रंग",
        "option_c": "ध्वनि",
        "option_d": "प्रकाश",
        "correct_answer": "B",
    }
    ok, reason = validate_quiz_question(translated, original)
    assert ok is True
    assert reason == ""


def test_validate_quiz_payload_count_mismatch():
    ok, reason = validate_quiz_payload([], [{"question": "Q"}])
    assert ok is False
    assert "count" in reason.lower()
