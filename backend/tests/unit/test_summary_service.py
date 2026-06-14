"""Unit tests for summary service."""

from services.summary_service import build_document_summary_from_chunks
from services.summary_parser import count_paragraphs


def test_build_document_summary_from_chunks():
    chunks = [
        "A continuous and closed path of an electric current is called an electric circuit.",
        "A component used to regulate current without changing the voltage source is called variable resistance.",
        "A conductor having some appreciable resistance is called a resistor.",
    ]
    payload = build_document_summary_from_chunks(chunks, "Electricity", grade=10)
    assert payload["summary"]
    assert payload["format_version"] == "v2-prose"
    assert count_paragraphs(payload["summary"]) >= 2
    assert "overview" not in payload
    assert "key_concepts" not in payload
