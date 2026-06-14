"""Unit tests for summary source filtering."""

from services.summary_context import filter_summary_source_chunks, strip_activity_passages


def test_strip_activity_passages_removes_activity_block():
    text = (
        "Electricity has an important place in modern society. "
        "Activity 6.1: Let us try an experiment with bulbs. "
        "Take two pipes and fill them with water. "
        "Ohm's law relates voltage, current, and resistance."
    )
    cleaned = strip_activity_passages(text)
    assert "Activity 6.1" not in cleaned
    assert "Ohm's law" in cleaned


def test_filter_summary_source_chunks_skips_activity_heavy_chunk():
    chunks = [
        "Activity 6.1: Let us try\nAim: study pressure\nProcedure: take pipes\n" * 5,
        "Electric current is the flow of charge. "
        "A closed path is called an electric circuit. "
        "The SI unit of electric charge is the coulomb.",
    ]
    filtered = filter_summary_source_chunks(chunks)
    assert len(filtered) == 1
    assert "electric circuit" in filtered[0].lower()


def test_filter_summary_source_chunks_keeps_short_definition_chunks():
    chunks = [
        "A continuous and closed path of an electric current is called an electric circuit.",
        "A conductor having some appreciable resistance is called a resistor.",
    ]
    filtered = filter_summary_source_chunks(chunks)
    assert len(filtered) == 2


def test_filter_summary_source_chunks_strips_story_characters():
    chunks = [
        (
            "Bhavisha and Dhruv activated Itihāsa, their time machine. "
            "What is an Empire? An empire is a collection of smaller kingdoms or territories "
            "over which a powerful ruler exerts power."
        )
    ]
    filtered = filter_summary_source_chunks(chunks)
    assert len(filtered) == 1
    assert "Bhavisha" not in filtered[0]
    assert "empire is a collection" in filtered[0].lower()
