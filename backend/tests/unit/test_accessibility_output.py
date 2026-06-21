"""Unit tests for accessibility output payloads."""

from config.constants import AccessibilityProfile
from services.accessibility_output import (
    build_accessibility_payload,
    enrich_response_data,
    format_text_for_profile,
)


def test_build_accessibility_payload_dyslexia():
    payload = build_accessibility_payload(
        AccessibilityProfile.DYSLEXIA,
        "Photosynthesis is how plants make food using sunlight and chlorophyll in leaves.",
    )
    assert payload["profile"] == "dyslexia"
    assert "•" in payload["formatted_text"]
    assert payload["reading_segments"]
    assert payload["audio_path"] is None


def test_build_accessibility_payload_include_audio_graceful(monkeypatch):
    def _fail(_text: str, *, segments=None):
        from exceptions import ServiceUnavailableError

        raise ServiceUnavailableError("Piper not configured.")

    monkeypatch.setattr("services.accessibility_output.generate_audio", _fail)
    payload = build_accessibility_payload(
        AccessibilityProfile.DYSLEXIA,
        "The Sun gives light.",
        include_audio=True,
    )
    assert payload["audio_path"] is None


def test_enrich_response_data_replaces_answer():
    data = enrich_response_data(
        {"answer": "Plants make food using sunlight through photosynthesis in green leaves."},
        "answer",
        AccessibilityProfile.DYSLEXIA,
    )
    assert "accessibility" in data
    assert "•" in data["answer"]
    assert data["accessibility"]["profile"] == "dyslexia"


def test_format_text_for_profile_noop_for_none():
    text = "Plain answer."
    assert format_text_for_profile(text, AccessibilityProfile.BEGINNER) == text
