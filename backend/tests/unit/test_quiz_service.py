"""Unit tests for quiz generation service."""

import json

import pytest

from services.quiz_service import (
    clamp_question_count,
    dedupe_questions,
    normalize_questions,
    parse_quiz_response,
    parse_quiz_text_response,
    validate_question_batch,
)


def test_clamp_question_count_defaults_and_bounds():
    assert clamp_question_count(None) == 10
    assert clamp_question_count(3) == 5
    assert clamp_question_count(20) == 15
    assert clamp_question_count(8) == 8


def test_parse_quiz_text_response_handles_numbered_blocks():
    raw = """Question 1: What is myopia?
A. Near-sightedness
B. Far-sightedness
C. Colour blindness
D. Night blindness
Answer: A

Question 2: Which lens corrects myopia?
A. Concave lens
B. Convex lens
C. Plane mirror
D. Convex mirror
Answer: A"""
    parsed = parse_quiz_text_response(raw)
    assert len(parsed) == 2
    assert parsed[0]["correct_answer"] == "A"
    assert parsed[1]["option_a"] == "Concave lens"


def test_parse_quiz_response_prefers_plain_text():
    raw = """Question 1: What is force?
A. Push or pull
B. Colour
C. Heat
D. Light
Answer: A"""
    parsed = parse_quiz_response(raw)
    assert len(parsed) == 1
    assert parsed[0]["question"] == "What is force?"


def test_parse_quiz_response_handles_fenced_json():
    raw = """Here is the quiz:
```json
{"questions": [{"question": "Q1?", "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D", "correct_answer": "B"}]}
```"""
    parsed = parse_quiz_response(raw)
    assert len(parsed) == 1


def test_parse_quiz_response_handles_truncated_outer_object():
    raw = """{"questions": [
  {"question": "Q1?", "option_a": "A1", "option_b": "B1", "option_c": "C1", "option_d": "D1"},
  {"question": "Q2?", "option_a": "A2", "option_b": "B2", "option_c": "C2", "option_d": "D2"}
]"""
    parsed = parse_quiz_response(raw)
    assert len(parsed) == 2


def test_parse_quiz_response_handles_string_encoded_questions():
    inner = (
        '[{"question": "Q1?", "option_a": "A1", "option_b": "B1", '
        '"option_c": "C1", "option_d": "D1", "correct_answer": "A"}]'
    )
    raw = json.dumps({"questions": inner})
    parsed = parse_quiz_response(raw)
    assert len(parsed) == 1


def test_parse_quiz_response_merges_duplicate_question_arrays():
    raw = """{ "questions": [ {"question": "Q1?", "option_a": "A1", "option_b": "B1", "option_c": "C1", "option_d": "D1", "correct_answer": "A"} ],
 "questions": [ {"question": "Q2?", "option_a": "A2", "option_b": "B2", "option_c": "C2", "option_d": "D2", "correct_answer": "B"} ],
 "questions": [ {"question": "Q3?", "option_a": "A3", "option_b": "B3", "option_c": "C3", "option_d": "D3", "correct_answer": "C"} ] }"""
    parsed = parse_quiz_response(raw)
    assert len(parsed) == 3


def test_normalize_questions_requires_all_options():
    raw = [
        {
            "question": "What is force?",
            "option_a": "Push or pull",
            "option_b": "Color",
            "option_c": "Heat",
            "option_d": "Light",
            "correct_answer": "A",
        },
        {
            "question": "Incomplete question?",
            "option_a": "Only one",
            "option_b": "",
            "option_c": "",
            "option_d": "",
            "correct_answer": "A",
        },
    ]
    normalized = normalize_questions(raw)
    assert len(normalized) == 1
    assert normalized[0]["options"]["A"] == "Push or pull"


def test_dedupe_questions_removes_duplicates():
    questions = [
        {"question": "Same question?", "options": {}, "correct_answer": "A"},
        {"question": "Same   question?", "options": {}, "correct_answer": "B"},
        {"question": "Different question?", "options": {}, "correct_answer": "C"},
    ]
    assert len(dedupe_questions(questions)) == 2


def test_validate_question_batch_enforces_minimum():
    with pytest.raises(Exception):
        validate_question_batch(
            [{"question": "Only one?", "options": {"A": "1", "B": "2", "C": "3", "D": "4"}, "correct_answer": "A"}],
            minimum=5,
            maximum=10,
        )


def test_generate_questions_for_context_retries_until_enough(monkeypatch):
    """Merge valid JSON from multiple LLM calls when each call returns partial output."""
    import json

    from ai.llm import set_llm
    from services.quiz_service import _generate_questions_for_context

    calls = {"count": 0}

    class PartialMockLLM:
        def generate(self, prompt: str, num_predict: int | None = None, format_json: bool = False):
            calls["count"] += 1
            idx = calls["count"]
            return json.dumps(
                {
                    "questions": [
                        {
                            "question": f"Question {idx} about resources and development?",
                            "option_a": "Resources and development",
                            "option_b": "Sports and games",
                            "option_c": "Music and dance",
                            "option_d": "Fashion and design",
                            "correct_answer": "A",
                        }
                    ]
                }
            )

    set_llm(PartialMockLLM())
    monkeypatch.setattr("services.quiz_service.settings.quiz_llm_max_attempts", 5)
    monkeypatch.setattr("services.quiz_service.settings.quiz_llm_batch_size", 1)

    questions = _generate_questions_for_context(
        "Chapter content about resources and development in India.",
        5,
        topic="Resources",
        grade=10,
        subject="Geography",
    )
    assert len(questions) == 5
    assert calls["count"] == 5
