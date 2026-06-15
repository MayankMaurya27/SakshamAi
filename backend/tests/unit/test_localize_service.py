"""Unit tests for Hinenglish localization service."""

from pathlib import Path

import pytest

from config.constants import LocalizeContentType
from services.localize_service import localize_to_hindi


@pytest.fixture
def localize_cache_dir(tmp_path, monkeypatch):
    cache_dir = tmp_path / "localize_cache"
    monkeypatch.setattr(
        "services.localize_cache.settings.localize_cache_dir",
        cache_dir,
    )
    monkeypatch.setattr(
        "services.localize_service.settings.localize_cache_dir",
        cache_dir,
    )
    return cache_dir


def test_localize_prose_returns_hindi_text(localize_cache_dir):
    result = localize_to_hindi(
        text="• Photosynthesis is the process by which plants make food.",
        content_type=LocalizeContentType.ANSWER,
        class_level=9,
    )
    assert result["language"] == "hi"
    assert result["content_type"] == "answer"
    assert "hindi_text" in result
    assert result["reading_segments"]
    assert result["cached"] is False


def test_localize_prose_uses_cache(localize_cache_dir):
    text = "Force is a push or pull on an object."
    first = localize_to_hindi(
        text=text,
        content_type=LocalizeContentType.SUMMARY,
    )
    second = localize_to_hindi(
        text=text,
        content_type=LocalizeContentType.SUMMARY,
    )
    assert first["cached"] is False
    assert second["cached"] is True
    assert first["hindi_text"] == second["hindi_text"]


def test_localize_quiz_returns_hindi_quiz(localize_cache_dir):
    quiz = {
        "questions": [
            {
                "question": "What is force?",
                "option_a": "Push or pull",
                "option_b": "Color",
                "option_c": "Sound",
                "option_d": "Light",
                "correct_answer": "A",
            }
        ]
    }
    result = localize_to_hindi(
        text=None,
        content_type=LocalizeContentType.QUIZ,
        quiz=quiz,
        class_level=8,
    )
    assert result["hindi_quiz"]["questions"][0]["correct_answer"] == "A"
    assert result["reading_segments"]


def test_localize_quiz_audio_skipped_without_model(localize_cache_dir, monkeypatch):
    def _fail_audio(*_args, **_kwargs):
        from exceptions import ServiceUnavailableError

        raise ServiceUnavailableError("Hindi Piper not configured.")

    monkeypatch.setattr("services.localize_service.generate_audio", _fail_audio)
    result = localize_to_hindi(
        text="• The Sun is a star.",
        content_type=LocalizeContentType.ANSWER,
        include_audio=True,
    )
    assert result["audio_path"] is None
