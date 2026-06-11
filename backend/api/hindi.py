"""Hindi explanation endpoint."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.responses import error_response, success_response
from api.schemas import LearningModeRequest
from config.constants import LearningMode
from database.db import get_db
from exceptions import DocumentNotFoundError, SakshamError, ServiceUnavailableError, ValidationError
from services.rag_service import answer_question

logger = logging.getLogger(__name__)
router = APIRouter(tags=["hindi"])


@router.post("/hindi")
def hindi_explanation(
    request: LearningModeRequest,
    db: Session = Depends(get_db),
):
    """Generate Hindi explanation for a question."""
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
        return success_response({"answer": answer})
    except DocumentNotFoundError as exc:
        return error_response(exc.message, status_code=404)
    except ValidationError as exc:
        return error_response(exc.message, status_code=422)
    except ServiceUnavailableError as exc:
        return error_response(exc.message, status_code=503)
    except SakshamError as exc:
        return error_response(exc.message, status_code=500)
