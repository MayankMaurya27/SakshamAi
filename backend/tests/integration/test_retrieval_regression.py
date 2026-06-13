"""Retrieval regression checks for known NCERT question/answer alignment."""

import pytest

from ai.context_cleaner import clean_context_for_llm, clean_context_text, trim_context_chunks
from ai.prompt_builder import format_retrieved_chunks
from ai.question_router import context_char_limit, resolve_answer_profile, retrieval_top_k
from ai.retriever import retrieve_saksham_context
from config.constants import AnswerProfile
from config.settings import get_settings


@pytest.mark.integration
def test_palampur_wages_retrieval_includes_minimum_wage_context():
    """Wages question should retrieve the Dala/minimum wage passage."""
    settings = get_settings()
    profile = resolve_answer_profile(
        "Why are the wages for farm labourers in Palampur less than minimum wages?"
    )
    contexts = retrieve_saksham_context(
        "Why are the wages for farm labourers in Palampur less than minimum wages?",
        class_level=9,
        subject="Economics",
        chapter_ref="The Story of Village Palampur",
        top_k=retrieval_top_k(profile, settings),
    )
    assert contexts
    texts = trim_context_chunks(
        [clean_context_for_llm(clean_context_text(c.text)) for c in contexts],
        max_chars=context_char_limit(profile, settings),
    )
    combined = format_retrieved_chunks(texts).lower()
    assert "minimum wage" in combined or "minimum wages" in combined
    assert "competition" in combined or "rs 160" in combined or "rs 300" in combined


@pytest.mark.integration
def test_palampur_electricity_retrieval_includes_irrigation_context():
    """Electricity question should retrieve Persian wheels / tubewell passage."""
    settings = get_settings()
    profile = resolve_answer_profile(
        "How did the spread of electricity help farmers in Palampur?"
    )
    contexts = retrieve_saksham_context(
        "How did the spread of electricity help farmers in Palampur?",
        class_level=9,
        subject="Economics",
        chapter_ref="The Story of Village Palampur",
        top_k=retrieval_top_k(profile, settings),
    )
    assert contexts
    texts = trim_context_chunks(
        [clean_context_for_llm(clean_context_text(c.text)) for c in contexts],
        max_chars=context_char_limit(profile, settings),
    )
    combined = format_retrieved_chunks(texts).lower()
    assert "electricity" in combined
    assert "tubewell" in combined or "persian" in combined or "irrigation" in combined
