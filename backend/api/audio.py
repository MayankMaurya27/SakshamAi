"""Audio generation endpoint."""

import logging

from fastapi import APIRouter

from api.responses import error_response, success_response
from api.schemas import AudioRequest
from exceptions import SakshamError, ServiceUnavailableError, ValidationError
from services.audio_service import generate_audio

logger = logging.getLogger(__name__)
router = APIRouter(tags=["audio"])


@router.post("/audio")
def create_audio(request: AudioRequest):
    """Convert text to speech using Piper TTS."""
    try:
        result = generate_audio(request.text)
        return success_response(result)
    except ValidationError as exc:
        return error_response(exc.message, status_code=422)
    except ServiceUnavailableError as exc:
        return error_response(exc.message, status_code=503)
    except SakshamError as exc:
        return error_response(exc.message, status_code=500)
