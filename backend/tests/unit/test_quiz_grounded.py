"""Unit tests for generic grounded quiz generation."""

from services.quiz_grounded import (
    _build_mcq,
    build_grounded_chapter_questions,
    extract_definition_questions,
    extract_sentence_cloze_questions,
    filter_grounded_questions,
    verify_grounded_question,
)


def test_build_mcq_rejects_filler_distractors():
    item = _build_mcq(
        "Sample question?",
        "Correct answer",
        wrong=["Option 1", "Option 2", "Option 3"],
    )
    assert item is None


def test_extract_definition_questions_from_generic_text():
    chunks = [
        "The portion of the circular region enclosed by two radii is called a sector of the circle.",
        "Myopia is also known as near-sightedness.",
    ]
    pool = ["another concept", "different term", "other phrase", "extra detail"]
    questions = extract_definition_questions(chunks, 2, set(), pool)
    corpus = "\n".join(chunks)
    verified = filter_grounded_questions(questions, corpus)
    assert len(verified) >= 1
    assert all(len(q["options"]) == 4 for q in verified)
    assert all(
        not opt.startswith("Option ")
        for q in verified
        for opt in q["options"].values()
    )


def test_build_grounded_chapter_questions_reaches_count_from_sentences():
    chunks = [
        "Agriculture is a primary activity that provides food and raw materials across India.",
        "Rice and wheat are major crops grown in different seasons across many states.",
        "Organic farming reduces the use of chemical fertilisers and pesticides in crop production.",
        "Irrigation helps farmers grow crops in areas with low rainfall throughout the year.",
        "Crop rotation improves soil fertility and reduces pest problems on farmland.",
        "Plantation farming is called a type of commercial agriculture in many regions.",
    ]
    questions = build_grounded_chapter_questions(chunks, 5, chapter_title="Agriculture")
    corpus = "\n".join(chunks)
    verified = filter_grounded_questions(questions, corpus)
    assert len(verified) >= 5


def test_verify_rejects_garbage_cloze_options():
    corpus = "Electricity has an important place in modern society."
    bad = {
        "question": "Complete the statement: E ______ in modern society.",
        "options": {
            "A": "V V1 V2 V3 11",
            "B": "lectricity has an important place",
            "C": "Option 1",
            "D": "Option 2",
        },
        "correct_answer": "B",
        "_quiz_meta": {
            "source_text": corpus,
            "source_type": "cloze",
        },
    }
    assert not verify_grounded_question(bad, corpus)


def test_electricity_definitions_without_filler_options():
    chunks = [
        "A continuous and closed path of an electric current is called an electric circuit.",
        "A component used to regulate current without changing the voltage source is called variable resistance.",
        "A conductor having some appreciable resistance is called a resistor.",
        "Electricity has an important place in modern society.",
        "It is a controllable and convenient form of energy for a variety of uses in homes and schools.",
    ]
    questions = build_grounded_chapter_questions(
        chunks,
        5,
        chapter_title="Electricity",
        allow_cloze=False,
    )
    corpus = "\n".join(chunks)
    verified = filter_grounded_questions(questions, corpus)
    assert len(verified) >= 3
    for q in verified:
        assert all(not v.startswith("Option ") for v in q["options"].values())
        assert all("V V1" not in v for v in q["options"].values())
