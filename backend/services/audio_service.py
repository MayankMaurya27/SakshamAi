"""Text-to-speech service using Piper TTS."""

from __future__ import annotations

import logging
import re
import subprocess
import tempfile
import uuid
import wave
from pathlib import Path

from ai.dyslexia_formatter import (
    build_pointwise_speech_lines,
    extract_speech_points,
    prepare_segment_for_speech,
)
from config.settings import get_settings
from exceptions import ServiceUnavailableError, ValidationError

logger = logging.getLogger(__name__)
settings = get_settings()

_piper_voice = None
_POINTWISE_PAUSE_MS = 750


def _text_for_speech(text: str) -> str:
    """Normalize plain text for clearer speech."""
    cleaned = text.replace("•", " ")
    cleaned = re.sub(r"^\d+[.)]\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.replace("\n\n", ". ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return prepare_segment_for_speech(cleaned) or cleaned


def _resolve_model_path() -> Path:
    configured = settings.piper_model_path.strip()
    if configured:
        path = Path(configured)
        if not path.is_absolute():
            path = settings.base_dir / path
        return path
    return settings.models_dir / "piper" / "en_US-lessac-medium.onnx"


def _load_piper_voice():
    global _piper_voice
    if _piper_voice is not None:
        return _piper_voice

    try:
        from piper import PiperVoice
    except ImportError as exc:
        raise ServiceUnavailableError(
            "Piper Python package not installed. Run: pip install piper-tts piper-phonemize-cross onnxruntime pathvalidate"
        ) from exc

    model_path = _resolve_model_path()
    if not model_path.exists():
        raise ServiceUnavailableError(
            f"Piper model not found at {model_path}. Run: python scripts/download_piper.py"
        )

    logger.info("Loading Piper voice model from %s", model_path)
    _piper_voice = PiperVoice.load(str(model_path))
    return _piper_voice


def _synthesize_single_line(voice, line: str, output_path: Path) -> wave._wave_params:
    with wave.open(str(output_path), "wb") as wav_file:
        voice.synthesize_wav(line, wav_file)
    with wave.open(str(output_path), "rb") as wav_file:
        return wav_file.getparams()


def _synthesize_pointwise(speech_lines: list[str], output_path: Path) -> None:
    """Synthesize each point separately and join with silent gaps."""
    if not speech_lines:
        raise ServiceUnavailableError("No speech points to synthesize.")

    voice = _load_piper_voice()
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


def _generate_with_python(text: str, output_path: Path) -> None:
    voice = _load_piper_voice()
    speech_text = _text_for_speech(text)
    with wave.open(str(output_path), "wb") as wav_file:
        voice.synthesize_wav(speech_text, wav_file)


def _generate_with_binary(text: str, output_path: Path, model_path: Path) -> None:
    process = subprocess.run(
        [
            settings.piper_binary,
            "--model",
            str(model_path),
            "--output_file",
            str(output_path),
        ],
        input=_text_for_speech(text),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if process.returncode != 0:
        logger.error("Piper TTS failed: %s", process.stderr)
        raise ServiceUnavailableError(f"Piper TTS failed: {process.stderr}")


def generate_audio(text: str, *, segments: list[str] | None = None) -> dict:
    """
    Convert text to speech using Piper TTS (Python API, binary fallback).

    When ``segments`` are provided, or the text is bullet/numbered list-like,
    each point is spoken as "Point 1.", "Point 2.", etc. with pauses between.

    Returns:
        Dict with audio_path and filename.

    Raises:
        ValidationError: If text is empty.
        ServiceUnavailableError: If Piper is not available.
    """
    if not text.strip():
        raise ValidationError("Text cannot be empty for audio generation.")

    model_path = _resolve_model_path()
    if not model_path.exists():
        raise ServiceUnavailableError(
            f"Piper model not found at {model_path}. Run: python scripts/download_piper.py"
        )

    speech_points = [segment.strip() for segment in (segments or []) if segment.strip()]
    if not speech_points:
        speech_points = extract_speech_points(text)
    use_pointwise = len(speech_points) > 1

    filename = f"{uuid.uuid4().hex}.wav"
    output_path = settings.audio_dir / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if use_pointwise:
            speech_lines = build_pointwise_speech_lines(speech_points)
            _synthesize_pointwise(speech_lines, output_path)
        else:
            _generate_with_python(text, output_path)
    except ServiceUnavailableError:
        raise
    except Exception as exc:
        logger.warning("Piper Python synthesis failed (%s); trying binary", exc)
        if use_pointwise:
            raise ServiceUnavailableError(
                "Point-wise audio requires the Piper Python package."
            ) from exc
        try:
            _generate_with_binary(text, output_path, model_path)
        except FileNotFoundError as bin_exc:
            raise ServiceUnavailableError(
                f"Piper binary '{settings.piper_binary}' not found and Python synthesis failed."
            ) from bin_exc

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise ServiceUnavailableError("Piper TTS did not produce output file.")

    logger.info(
        "Generated audio file: %s (%s)",
        filename,
        "point-wise" if use_pointwise else "continuous",
    )
    return {
        "audio_path": f"/audio/{filename}",
        "filename": filename,
    }


def reset_piper_voice_for_testing() -> None:
    """Clear cached Piper voice (tests only)."""
    global _piper_voice
    _piper_voice = None
