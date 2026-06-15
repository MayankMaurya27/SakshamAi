"""Text-to-speech service using Piper TTS."""

from __future__ import annotations

import logging
import re
import subprocess
import tempfile
import uuid
import wave
from pathlib import Path
from typing import Literal

from ai.dyslexia_formatter import (
    build_pointwise_speech_lines,
    extract_speech_points as extract_english_speech_points,
    prepare_segment_for_speech as prepare_english_segment_for_speech,
)
from ai.hindi_formatter import (
    build_hindi_pointwise_speech_lines,
    extract_speech_points as extract_hindi_speech_points,
    prepare_segment_for_speech as prepare_hindi_segment_for_speech,
)
from config.settings import get_settings
from exceptions import ServiceUnavailableError, ValidationError

logger = logging.getLogger(__name__)
settings = get_settings()

_piper_voices: dict[str, object] = {}
_POINTWISE_PAUSE_MS = 750
AudioLanguage = Literal["en", "hi"]


def _text_for_speech(text: str, language: AudioLanguage = "en") -> str:
    """Normalize plain text for clearer speech."""
    cleaned = text.replace("•", " ")
    cleaned = re.sub(r"^\d+[.)]\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.replace("\n\n", ". ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if language == "hi":
        return prepare_hindi_segment_for_speech(cleaned) or cleaned
    return prepare_english_segment_for_speech(cleaned) or cleaned


def _resolve_model_path(language: AudioLanguage = "en") -> Path:
    if language == "hi":
        configured = settings.piper_hindi_model_path.strip()
        default_name = "hi_IN-rohan-medium.onnx"
    else:
        configured = settings.piper_model_path.strip()
        default_name = "en_US-lessac-medium.onnx"

    if configured:
        path = Path(configured)
        if not path.is_absolute():
            path = settings.base_dir / path
        return path
    return settings.models_dir / "piper" / default_name


def _load_piper_voice(language: AudioLanguage = "en"):
    if language in _piper_voices:
        return _piper_voices[language]

    try:
        from piper import PiperVoice
    except ImportError as exc:
        raise ServiceUnavailableError(
            "Piper Python package not installed. Run: pip install piper-tts piper-phonemize-cross onnxruntime pathvalidate"
        ) from exc

    model_path = _resolve_model_path(language)
    if not model_path.exists():
        script_hint = "python scripts/download_piper.py"
        if language == "hi":
            script_hint += " --hindi"
        raise ServiceUnavailableError(
            f"Piper model not found at {model_path}. Run: {script_hint}"
        )

    logger.info("Loading Piper voice model (%s) from %s", language, model_path)
    _piper_voices[language] = PiperVoice.load(str(model_path))
    return _piper_voices[language]


def _synthesize_single_line(voice, line: str, output_path: Path) -> wave._wave_params:
    with wave.open(str(output_path), "wb") as wav_file:
        voice.synthesize_wav(line, wav_file)
    with wave.open(str(output_path), "rb") as wav_file:
        return wav_file.getparams()


def _synthesize_pointwise(
    speech_lines: list[str],
    output_path: Path,
    language: AudioLanguage = "en",
) -> None:
    """Synthesize each point separately and join with silent gaps."""
    if not speech_lines:
        raise ServiceUnavailableError("No speech points to synthesize.")

    voice = _load_piper_voice(language)
    sample_rate = voice.config.sample_rate
    pause_frames = int(sample_rate * _POINTWISE_PAUSE_MS / 1000)
    silence = b"\x00\x00" * pause_frames

    wav_params = None
    audio_chunks: list[bytes] = []

    for index, line in enumerate(speech_lines):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            wav_params = _synthesize_single_line(voice, line, tmp_path)
            with wave.open(str(tmp_path), "rb") as wav_file:
                audio_chunks.append(wav_file.readframes(wav_file.getnframes()))
        finally:
            tmp_path.unlink(missing_ok=True)

        if index < len(speech_lines) - 1:
            audio_chunks.append(silence)

    if wav_params is None:
        raise ServiceUnavailableError("Piper TTS did not produce output file.")

    with wave.open(str(output_path), "wb") as out_file:
        out_file.setparams(wav_params)
        for chunk in audio_chunks:
            out_file.writeframes(chunk)


def _generate_with_python(
    text: str,
    output_path: Path,
    language: AudioLanguage = "en",
) -> None:
    voice = _load_piper_voice(language)
    speech_text = _text_for_speech(text, language=language)
    with wave.open(str(output_path), "wb") as wav_file:
        voice.synthesize_wav(speech_text, wav_file)


def _generate_with_binary(
    text: str,
    output_path: Path,
    model_path: Path,
    language: AudioLanguage = "en",
) -> None:
    process = subprocess.run(
        [
            settings.piper_binary,
            "--model",
            str(model_path),
            "--output_file",
            str(output_path),
        ],
        input=_text_for_speech(text, language=language),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if process.returncode != 0:
        logger.error("Piper TTS failed: %s", process.stderr)
        raise ServiceUnavailableError(f"Piper TTS failed: {process.stderr}")


def _speech_points_for_text(
    text: str,
    segments: list[str] | None,
    language: AudioLanguage,
) -> list[str]:
    speech_points = [segment.strip() for segment in (segments or []) if segment.strip()]
    if speech_points:
        return speech_points
    if language == "hi":
        return extract_hindi_speech_points(text)
    return extract_english_speech_points(text)


def _pointwise_speech_lines(
    speech_points: list[str],
    language: AudioLanguage,
) -> list[str]:
    if language == "hi":
        return build_hindi_pointwise_speech_lines(speech_points)
    return build_pointwise_speech_lines(speech_points)


def generate_audio(
    text: str,
    *,
    segments: list[str] | None = None,
    language: AudioLanguage = "en",
) -> dict:
    """
    Convert text to speech using Piper TTS (Python API, binary fallback).

    When ``segments`` are provided, or the text is bullet/numbered list-like,
    each point is spoken with pauses between (Point N / बिंदु N).

    Returns:
        Dict with audio_path and filename.

    Raises:
        ValidationError: If text is empty.
        ServiceUnavailableError: If Piper is not available.
    """
    if not text.strip():
        raise ValidationError("Text cannot be empty for audio generation.")

    model_path = _resolve_model_path(language)
    if not model_path.exists():
        script_hint = "python scripts/download_piper.py"
        if language == "hi":
            script_hint += " --hindi"
        raise ServiceUnavailableError(
            f"Piper model not found at {model_path}. Run: {script_hint}"
        )

    speech_points = _speech_points_for_text(text, segments, language)
    use_pointwise = len(speech_points) > 1

    filename = f"{uuid.uuid4().hex}.wav"
    output_path = settings.audio_dir / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if use_pointwise:
            speech_lines = _pointwise_speech_lines(speech_points, language)
            _synthesize_pointwise(speech_lines, output_path, language=language)
        else:
            _generate_with_python(text, output_path, language=language)
    except ServiceUnavailableError:
        raise
    except Exception as exc:
        logger.warning("Piper Python synthesis failed (%s); trying binary", exc)
        if use_pointwise:
            raise ServiceUnavailableError(
                "Point-wise audio requires the Piper Python package."
            ) from exc
        try:
            _generate_with_binary(text, output_path, model_path, language=language)
        except FileNotFoundError as bin_exc:
            raise ServiceUnavailableError(
                f"Piper binary '{settings.piper_binary}' not found and Python synthesis failed."
            ) from bin_exc

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise ServiceUnavailableError("Piper TTS did not produce output file.")

    logger.info(
        "Generated audio file: %s (%s, %s)",
        filename,
        language,
        "point-wise" if use_pointwise else "continuous",
    )
    return {
        "audio_path": f"/audio/{filename}",
        "filename": filename,
    }


def reset_piper_voice_for_testing() -> None:
    """Clear cached Piper voices (tests only)."""
    _piper_voices.clear()
