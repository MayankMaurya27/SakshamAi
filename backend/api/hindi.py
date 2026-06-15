"""Hindi explanation endpoint (deprecated — use English endpoints + POST /localize/hi)."""

import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.accessibility_helpers import with_accessibility
from api.responses import error_response
from api.schemas import LearningModeRequest
from config.constants import LearningMode
from database.db import get_db
from exceptions import DocumentNotFoundError, SakshamError, ServiceUnavailableError, ValidationError
from services.rag_service import answer_question

logger = logging.getLogger(__name__)
router = APIRouter(tags=["hindi"])

DEPRECATION_MESSAGE = (
    "POST /hindi is deprecated. Use an English endpoint (e.g. POST /ask) "
    "then POST /localize/hi with the English text."
)


@router.post("/hindi")
def hindi_explanation(
    request: LearningModeRequest,
    db: Session = Depends(get_db),
):
    """Generate Hindi explanation for a question (deprecated)."""
    logger.warning("Deprecated endpoint POST /hindi called; migrate to POST /localize/hi")
    try:
        answer = answer_question(
            question=request.question,
            source=request.source,
            db=db,
            document_id=request.document_id,
            class_level=request.class_level,
            subject=request.subject,
            chapter=request.chapter,
            topic=request.topic,
            mode=LearningMode.HINDI,
            accessibility_profile=request.accessibility_profile,
        )
        data = with_accessibility(
            {"answer": answer},
            "answer",
            request.accessibility_profile,
            include_audio=request.include_audio,
            already_formatted=True,
        )
        data["deprecated"] = True
        data["migration"] = DEPRECATION_MESSAGE
        return JSONResponse(
            status_code=200,
            content={"success": True, "data": data},
            headers={"Deprecation": "true"},
        )
    except DocumentNotFoundError as exc:
        return error_response(exc.message, status_code=404)
    except ValidationError as exc:
        return error_response(exc.message, status_code=422)
    except ServiceUnavailableError as exc:
        return error_response(exc.message, status_code=503)
    except SakshamError as exc:
        return error_response(exc.message, status_code=500)
