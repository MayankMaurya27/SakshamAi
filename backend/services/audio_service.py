"""Text-to-speech service using Piper TTS."""

import logging
import subprocess
import uuid
from pathlib import Path

from config.settings import get_settings
from exceptions import ServiceUnavailableError, ValidationError

logger = logging.getLogger(__name__)
settings = get_settings()


def generate_audio(text: str) -> dict:
    """
    Convert text to speech using Piper TTS.

    Returns:
        Dict with audio_path and filename.

    Raises:
        ValidationError: If text is empty.
        ServiceUnavailableError: If Piper is not available.
    """
    if not text.strip():
        raise ValidationError("Text cannot be empty for audio generation.")

    if not settings.piper_model_path:
        raise ServiceUnavailableError(
            "Piper TTS model not configured. Set PIPER_MODEL_PATH in environment."
        )

    model_path = Path(settings.piper_model_path)
    if not model_path.exists():
        raise ServiceUnavailableError(f"Piper model not found at {model_path}")

    filename = f"{uuid.uuid4().hex}.wav"
    output_path = settings.audio_dir / filename

    try:
        process = subprocess.run(
            [
                settings.piper_binary,
                "--model",
                str(model_path),
                "--output_file",
                str(output_path),
            ],
            input=text,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except FileNotFoundError as exc:
        raise ServiceUnavailableError(
            f"Piper binary '{settings.piper_binary}' not found."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ServiceUnavailableError("Piper TTS timed out.") from exc

    if process.returncode != 0:
        logger.error("Piper TTS failed: %s", process.stderr)
        raise ServiceUnavailableError(f"Piper TTS failed: {process.stderr}")

    if not output_path.exists():
        raise ServiceUnavailableError("Piper TTS did not produce output file.")

    logger.info("Generated audio file: %s", filename)
    return {
        "audio_path": f"/audio/{filename}",
        "filename": filename,
    }
