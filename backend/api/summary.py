"""Summary generation endpoint."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.responses import error_response, success_response
from api.schemas import SummaryRequest
from database.db import get_db
from exceptions import DocumentNotFoundError, SakshamError, ServiceUnavailableError, ValidationError
from services.summary_service import generate_summary

logger = logging.getLogger(__name__)
router = APIRouter(tags=["summary"])


@router.post("/summary")
def create_summary(
    request: SummaryRequest,
    db: Session = Depends(get_db),
):
    """Generate or return a revision summary for a Saksham chapter or document."""
    try:
        result = generate_summary(
            source=request.source,
            db=db,
            regenerate=request.regenerate,
            document_id=request.document_id,
            class_level=request.class_level,
            subject=request.subject,
            chapter=request.chapter,
            topic=request.topic,
            accessibility_profile=request.accessibility_profile,
            include_audio=request.include_audio,
        )
        return success_response(result)
    except DocumentNotFoundError as exc:
        return error_response(exc.message, status_code=404)
    except ValidationError as exc:
        return error_response(exc.message, status_code=422)
    except ServiceUnavailableError as exc:
        return error_response(exc.message, status_code=503)
    except SakshamError as exc:
        return error_response(exc.message, status_code=500)
