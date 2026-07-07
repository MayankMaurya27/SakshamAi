"""Voice Assistant NLU parsing endpoint."""

import logging
from fastapi import APIRouter

from api.responses import error_response, success_response
from api.schemas import VoiceParseRequest, VoiceParseResponse
from exceptions import SakshamError, ValidationError
from services.voice_service import parse_transcript

logger = logging.getLogger(__name__)
router = APIRouter(tags=["voice"])

@router.post("/voice/parse")
def parse_voice_command(request: VoiceParseRequest):
    """Parse a student voice transcript to identify intent and parameters."""
    try:
        result = parse_transcript(
            transcript=request.transcript,
            current_class=request.class_level,
            current_subject=request.subject,
            current_chapter=request.chapter,
        )
        return success_response(result)
    except ValidationError as exc:
        return error_response(exc.message, status_code=422)
    except SakshamError as exc:
        return error_response(exc.message, status_code=500)
    except Exception as exc:
        logger.error("Unhandled error in /voice/parse: %s", exc)
        return error_response("An unhandled voice processing error occurred.", status_code=500)
