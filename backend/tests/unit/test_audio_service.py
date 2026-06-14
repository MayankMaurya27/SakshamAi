"""Unit tests for point-wise audio generation."""

from pathlib import Path

import pytest

from services.audio_service import generate_audio, reset_piper_voice_for_testing


@pytest.fixture(autouse=True)
def _reset_voice_cache():
    reset_piper_voice_for_testing()
    yield
    reset_piper_voice_for_testing()


def test_generate_audio_pointwise_uses_numbered_lines(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "services.audio_service.settings.audio_dir",
        tmp_path,
    )
    monkeypatch.setattr(
        "services.audio_service._resolve_model_path",
        lambda: tmp_path / "model.onnx",
    )
    (tmp_path / "model.onnx").write_bytes(b"x")

    captured_lines: list[str] = []

    def fake_pointwise(lines, output_path: Path):
        captured_lines.extend(lines)
        output_path.write_bytes(b"RIFF")

    monkeypatch.setattr("services.audio_service._synthesize_pointwise", fake_pointwise)

    bullet_text = (
        "• Photosynthesis [process by which plants make food]\n\n"
        "• uses sunlight [energy from the sun]"
    )
    result = generate_audio(bullet_text)

    assert captured_lines == [
        "Point 1. Photosynthesis. process by which plants make food.",
        "Point 2. uses sunlight. energy from the sun.",
    ]
    assert result["audio_path"].startswith("/audio/")


def test_generate_audio_plain_text_stays_continuous(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "services.audio_service.settings.audio_dir",
        tmp_path,
    )
    monkeypatch.setattr(
        "services.audio_service._resolve_model_path",
        lambda: tmp_path / "model.onnx",
    )
    (tmp_path / "model.onnx").write_bytes(b"x")

    called = {"pointwise": False, "python": False}

    def fake_pointwise(_lines, _output_path):
        called["pointwise"] = True

    def fake_python(_text, _output_path):
        called["python"] = True
        _output_path.write_bytes(b"RIFF")

    monkeypatch.setattr("services.audio_service._synthesize_pointwise", fake_pointwise)
    monkeypatch.setattr("services.audio_service._generate_with_python", fake_python)

    generate_audio("One short sentence.")

    assert called["python"] is True
    assert called["pointwise"] is False
