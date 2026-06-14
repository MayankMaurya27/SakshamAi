"""Unit tests for summary service."""

from services.summary_service import build_document_summary_from_chunks
from services.summary_parser import count_paragraphs, count_words


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
    assert count_words(payload["summary"]) >= 35


def test_short_upload_summary_never_empty():
    chunks = ["Force is a push or pull. Newton studied force and motion."]
    payload = build_document_summary_from_chunks(chunks, "force.pdf", grade=8)
    assert payload["summary"].strip()
    assert "force" in payload["summary"].lower()
