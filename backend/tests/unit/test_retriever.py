"""Unit tests for retrieval helpers."""

from ai.retriever import get_search_terms


def test_search_terms_include_content_phrases_for_electricity_question():
    terms = get_search_terms(
        "How did the spread of electricity help farmers in Palampur?"
    )
    lowered = [term.lower() for term in terms]
    assert "palampur" in lowered
    assert any("electricity" in term for term in lowered)


def test_search_terms_include_minimum_wages_phrase():
    terms = get_search_terms(
        "Why are the wages for farm labourers in Palampur less than minimum wages?"
    )
    lowered = [term.lower() for term in terms]
    assert "minimum wages" in lowered or "farm labourers" in lowered
