"""Unit tests for math quiz helpers."""

from services.quiz_math import (
    build_chapter_quiz_questions,
    build_concept_questions,
    build_fact_questions,
    detect_math_chapter_kind,
    extract_valid_math_facts,
    filter_math_questions,
    is_math_subject,
    is_valid_math_question,
)


def test_is_math_subject():
    assert is_math_subject("Mathematics")
    assert not is_math_subject("Geography")


def test_detect_math_chapter_kind_from_title():
    assert detect_math_chapter_kind([], "ARITHMETIC EXPRESSIONS") == "expressions"
    assert detect_math_chapter_kind([], "A TALE OF THREE INTERSECTING LINES") == "geometry"


def test_extract_valid_math_facts_validates_results():
    chunks = [
        "Examples: 24 ÷ 100 = 0.24 678 ÷ 1000 = 0.678",
        "Bad OCR: 9.5 × 5 = 9.5",
        "Valid product: 18 × 12 = 216",
        "Addition: 16 + 37 = 53",
    ]
    facts = extract_valid_math_facts(chunks)
    assert len(facts) == 4
    assert any(fact.operator == "+" for fact in facts)


def test_build_fact_questions_uses_expression_framing():
    chunks = ["Addition: 11749 + 9055 = 20804", "Valid product: 7 × 5 = 35"]
    facts = extract_valid_math_facts(chunks)
    questions = build_fact_questions(facts, 2, chapter_kind="expressions")
    assert "value of the expression" in questions[0]["question"]
    assert "11749" in questions[0]["question"]


def test_build_concept_questions_for_geometry_chapter():
    chunks = [
        "Which lengths can be sidelengths of a triangle? (a) 2, 2, 5 (b) 3, 4, 6 (c) 2, 4, 8",
        "Triangles having all three equal sides are called equilateral triangles.",
    ]
    questions = build_concept_questions(chunks, 2, "geometry")
    assert len(questions) == 2
    assert "triangle" in questions[0]["question"].lower()


def test_build_chapter_quiz_questions_avoids_geometry_in_expressions():
    chunks = [
        "Every arithmetic expression has a value which is the number it evaluates to.",
        "For example: 11749 + 9055 = 20804 and 16 + 37 = 53.",
        "The word angle appears here but this chapter is about expressions.",
    ]
    questions, kind = build_chapter_quiz_questions(chunks, 5, "ARITHMETIC EXPRESSIONS")
    assert kind == "expressions"
    assert len(questions) >= 3
    assert all("triangle" not in q["question"].lower() for q in questions)


def test_filter_math_questions_rejects_story_copy():
    good = {
        "question": "What is the value of the expression 24 ÷ 100?",
        "options": {"A": "0.24", "B": "2.4", "C": "0.024", "D": "24"},
        "correct_answer": "A",
    }
    bad = {
        "question": "Jonali and Pallabi play a game. Jonali says a fraction.",
        "options": {"A": "0.25", "B": "0.5", "C": "1.0", "D": "2.0"},
        "correct_answer": "A",
    }
    filtered = filter_math_questions([good, bad])
    assert filtered == [good]
    assert is_valid_math_question(good["question"], good["options"])
