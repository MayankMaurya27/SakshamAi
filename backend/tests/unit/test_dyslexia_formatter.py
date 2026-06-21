"""Unit tests for dyslexia text formatter."""

from ai.dyslexia_formatter import (
    build_pointwise_speech_lines,
    extract_preserve_terms,
    extract_speech_points,
    format_dyslexia_text,
    prepare_segment_for_speech,
    split_reading_segments,
)


def test_format_dyslexia_text_preserves_long_sentences_complete():
    text = (
        "Photosynthesis is the process by which green plants make food using sunlight, "
        "and it is one of the most important life processes on Earth for all living things."
    )
    formatted = format_dyslexia_text(text, max_words_per_sentence=12, max_bullets=6)
    assert "•" in formatted
    segments = split_reading_segments(formatted)
    assert len(segments) == 1
    assert "Photosynthesis is the process" in segments[0]


def test_format_dyslexia_text_strips_connectors():
    text = "Furthermore, plants need sunlight. Consequently, they make food."
    formatted = format_dyslexia_text(text, max_bullets=4)
    assert "Furthermore" not in formatted
    assert "Consequently" not in formatted


def test_format_dyslexia_text_respects_bullet_cap():
    text = ". ".join(f"Fact number {idx} is important for exams" for idx in range(1, 12))
    formatted = format_dyslexia_text(text, max_bullets=5)
    segments = split_reading_segments(formatted)
    assert len(segments) <= 5


def test_split_reading_segments_from_bullets():
    formatted = "• The Sun is a star.\n\n• Earth moves around the Sun."
    segments = split_reading_segments(formatted)
    assert segments == ["The Sun is a star.", "Earth moves around the Sun."]


def test_split_reading_segments_from_numbered_list():
    formatted = "1. The Sun is a star.\n2. Earth moves around the Sun."
    segments = split_reading_segments(formatted)
    assert segments == ["The Sun is a star.", "Earth moves around the Sun."]


def test_prepare_segment_for_speech_expands_brackets():
    spoken = prepare_segment_for_speech(
        "Photosynthesis [process by which plants make their own food]"
    )
    assert spoken == "Photosynthesis. process by which plants make their own food"


def test_build_pointwise_speech_lines_numbers_each_point():
    segments = [
        "Photosynthesis [process by which plants make food]",
        "uses sunlight [energy from the sun]",
    ]
    lines = build_pointwise_speech_lines(segments)
    assert lines == [
        "Photosynthesis. process by which plants make food.",
        "uses sunlight. energy from the sun.",
    ]


def test_extract_speech_points_from_bullets():
    text = "• One.\n\n• Two.\n\n• Three."
    assert extract_speech_points(text) == ["One.", "Two.", "Three."]


def test_extract_speech_points_from_numbered_list():
    text = "1. First item\n2. Second item"
    assert extract_speech_points(text) == ["First item", "Second item"]


def test_extract_speech_points_plain_text_is_single():
    assert extract_speech_points("One short sentence.") == ["One short sentence."]


def test_extract_preserve_terms():
    corpus = "Photosynthesis occurs in chloroplasts during daylight hours."
    terms = extract_preserve_terms(corpus)
    assert "Photosynthesis" in terms
    assert "chloroplasts" in terms


def _word_count(text: str) -> int:
    import re

    return len(re.findall(r"\b\w+\b", text))
