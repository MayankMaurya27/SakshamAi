"""Unit tests for summary text cleaning."""

from services.summary_parser import (
    clean_summary_text,
    count_paragraphs,
    dedupe_sentences,
    merge_partial_summaries,
    strip_legacy_section_headers,
)

LEGACY = """OVERVIEW
Electricity is an important form of energy used in daily life.

KEY CONCEPTS
Electric current: flow of electric charge through a conductor.
Voltage: energy per unit charge that drives current.

REVISION POINTS
- Current needs a closed circuit.
- Ohm's law links voltage, current, and resistance.
"""


def test_strip_legacy_section_headers():
    converted = strip_legacy_section_headers(LEGACY)
    assert "OVERVIEW" not in converted
    assert "Electricity is an important form of energy" in converted
    assert "Electric current" in converted


def test_clean_summary_text_builds_paragraphs():
    raw = (
        "Electric current is the flow of charge. "
        "A closed path is called an electric circuit. "
        "Potential difference drives current in the circuit."
    )
    cleaned = clean_summary_text(raw)
    assert count_paragraphs(cleaned) >= 2
    assert "electric circuit" in cleaned.lower()


def test_dedupe_sentences_removes_near_duplicates():
    repeated = (
        "Electric current is the flow of positive charges in a conducting metallic wire. "
        "Electric current is the flow of positive charges in a conductor. "
        "Electric potential difference is the work done to move a unit charge."
    )
    cleaned = dedupe_sentences(repeated)
    assert cleaned.count("Electric current is the flow") == 1
    assert "Electric potential difference" in cleaned


def test_merge_partial_summaries_deduplicates():
    part_a = (
        "Electric current flows through a conductor in a closed circuit.\n\n"
        "Potential difference is needed for current to flow."
    )
    part_b = (
        "Electric current moves through a closed circuit in a conductor.\n\n"
        "Resistance opposes the flow of current."
    )
    merged = merge_partial_summaries([part_a, part_b])
    assert count_paragraphs(merged) >= 2
    assert "Resistance opposes" in merged
