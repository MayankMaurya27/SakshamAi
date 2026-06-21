"""Unit tests for Hindi formatter helpers."""

from ai.hindi_formatter import (
    build_hindi_pointwise_speech_lines,
    devanagari_ratio,
    extract_preserve_terms_from_english,
    extract_speech_points,
    split_reading_segments,
)


def test_devanagari_ratio_for_hindi_text():
    text = "प्रकाश संश्लेषण (Photosynthesis) महत्वपूर्ण है।"
    assert devanagari_ratio(text) >= 0.5


def test_extract_preserve_terms_from_english():
    terms = extract_preserve_terms_from_english(
        "Photosynthesis uses chlorophyll and CO2 in leaves."
    )
    assert "Photosynthesis" in terms
    assert "chlorophyll" in terms


def test_split_reading_segments_bullets():
    text = "• पहला बिंदु।\n\n• दूसरा बिंदु।"
    segments = split_reading_segments(text)
    assert len(segments) == 2


def test_build_hindi_pointwise_speech_lines():
    lines = build_hindi_pointwise_speech_lines(["प्रकाश संश्लेषण महत्वपूर्ण है"])
    assert lines == ["प्रकाश संश्लेषण महत्वपूर्ण है."]


def test_extract_speech_points_multiple_bullets():
    text = "• एक।\n\n• दो।"
    assert extract_speech_points(text) == ["एक।", "दो।"]
