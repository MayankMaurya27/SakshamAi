"""Unit tests for biography sidebar extraction."""

from ai.bio_formatter import is_bio_question, try_format_bio_answer
from ai.retriever import extract_query_terms, get_search_terms, _keyword_match_score

MEGHNAD_PASSAGE = (
    "Ever heard of ... In 1952, the Government of India set up a Calendar Reform Committee. "
    "Be a scientist Meghnad Saha (1893 –1956) Meghnad Saha was a pioneering astrophysicist "
    "of India who studied stars and their temperatures and developed a mathematical equation, "
    "famously known as the Saha equation. The Saha Institute of Nuclear Physics, in Kolkata, "
    "is named after him. He was also the chairperson of the Calendar Reform Committee. "
    "11.3 Are Festivals Related to Astronomical Phenomena?"
)


def test_extract_query_terms_person_name():
    terms = extract_query_terms("who was Meghnad Saha")
    assert "Meghnad Saha" in terms


def test_keyword_match_score_prefers_full_name():
    terms = get_search_terms("who was Meghnad Saha")
    score = _keyword_match_score(MEGHNAD_PASSAGE, terms)
    assert score >= 3.5


def test_try_format_bio_answer_meghnad_saha():
    terms = extract_query_terms("who was Meghnad Saha")
    answer = try_format_bio_answer(MEGHNAD_PASSAGE, terms)
    assert answer is not None
    assert "astrophysicist" in answer
    assert "Saha equation" in answer
    assert "Calendar Reform Committee" in answer
    assert "beryllium" not in answer.lower()
    assert "nobel" not in answer.lower()


def test_is_bio_question():
    assert is_bio_question("who was Meghnad Saha")
    assert not is_bio_question("How are communicable diseases spread?")
    assert not is_bio_question("What was the French Revolution?")
