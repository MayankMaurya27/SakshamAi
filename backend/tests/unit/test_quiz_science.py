"""Unit tests for science quiz helpers."""

from services.quiz_science import (
    build_science_concept_questions,
    is_science_subject,
)


def test_is_science_subject():
    assert is_science_subject("Science")
    assert not is_science_subject("Geography")


def test_build_science_concept_questions_for_intro_chapter():
    chunks = [
        "You will read about topics in different fields of science, from physics and chemistry to biology and earth sciences.",
        "Early humans observed the shadows of objects in the Sun and used the position of the shadows to tell the time.",
        "something as simple as a paper plane inspired real scientific explorations of flight",
    ]
    questions = build_science_concept_questions(
        chunks,
        5,
        chapter_title="The Ever-Evolving World of Science",
    )
    assert len(questions) >= 3
    assert all("triangle" not in q["question"].lower() for q in questions)


def test_build_science_concept_questions_for_human_eye_chapter():
    chunks = [
        "There are mainly three common refractive defects of vision. These are (i) myopia or near-sightedness, "
        "(ii) Hypermetropia or far-sightedness, and (iii) Presbyopia.",
        "Myopia is also known as near-sightedness. A concave lens is used for correction for myopia.",
        "The splitting of light into its component colours is called dispersion.",
        "The red light bends the least while the violet the most.",
        "The ability of the eye lens to adjust its focal length is called accommodation.",
    ]
    questions = build_science_concept_questions(
        chunks,
        5,
        chapter_title="The Human Eye and the Colourful World",
    )
    assert len(questions) == 5


def test_build_science_concept_questions_for_heredity_chapter():
    chunks = [
        "A section of DNA that provides information for one protein is called the gene for that protein.",
        "Traits like 'T' are called dominant traits, while those that behave like 't' are called recessive traits.",
        "Mendel used a number of contrasting visible characters of garden peas.",
        "All plants were tall in the F1 progeny. In the F2, progeny one quarter of them are short.",
        "The number of successful variations are maximised by the process of sexual reproduction.",
        "Each separate independent pieces, each called a chromosome. Each cell will have two copies of each chromosome.",
    ]
    questions = build_science_concept_questions(
        chunks,
        5,
        chapter_title="Heredity and Evolution",
    )
    assert len(questions) == 5
    assert any("gene" in q["question"].lower() or "mendel" in q["question"].lower() for q in questions)
