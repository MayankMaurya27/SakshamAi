"""Hinenglish localization endpoint."""

import logging

from fastapi import APIRouter

from api.responses import error_response, success_response
from api.schemas import LocalizeHiRequest
from exceptions import SakshamError, ServiceUnavailableError, ValidationError
from services.localize_service import localize_to_hindi

logger = logging.getLogger(__name__)
router = APIRouter(tags=["localize"])


def _localize_response(
    *,
    text: str | None,
    content_type,
    quiz_payload: dict | None,
    class_level: int | None,
    subject: str | None,
    include_audio: bool,
    preserve_terms: list[str] | None,
):
    try:
        result = localize_to_hindi(
            text=text,
            content_type=content_type,
            quiz=quiz_payload,
            class_level=class_level,
            subject=subject,
            include_audio=include_audio,
            preserve_terms=preserve_terms,
        )
        return success_response(result)
    except ValidationError as exc:
        return error_response(exc.message, status_code=422)
    except ServiceUnavailableError as exc:
        return error_response(exc.message, status_code=503)
    except SakshamError as exc:
        return error_response(exc.message, status_code=500)


@router.post("/localize/hi")
def localize_hi(request: LocalizeHiRequest):
    """Convert English answer, summary, or quiz text into Hinenglish."""
    quiz_payload = None
    if request.quiz is not None:
        quiz_payload = {
            "questions": [question.model_dump() for question in request.quiz.questions]
        }
    return _localize_response(
        text=request.text,
        content_type=request.content_type,
        quiz_payload=quiz_payload,
        class_level=request.class_level,
        subject=request.subject,
        include_audio=request.include_audio,
        preserve_terms=request.preserve_terms,
    )
