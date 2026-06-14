"""Question answering endpoint."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.accessibility_helpers import with_accessibility
from api.responses import error_response, success_response
from api.schemas import AskRequest
from database.db import get_db
from exceptions import DocumentNotFoundError, SakshamError, ServiceUnavailableError, ValidationError
from services.rag_service import answer_question

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ask"])


@router.post("/ask")
def ask_question(
    request: AskRequest,
    db: Session = Depends(get_db),
):
    """Answer a question using RAG."""
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
            mode=request.mode,
            accessibility_profile=request.accessibility_profile,
        )
        data = with_accessibility(
            {"answer": answer},
            "answer",
            request.accessibility_profile,
            include_audio=request.include_audio,
            already_formatted=True,
        )
        return success_response(data)
    except DocumentNotFoundError as exc:
        return error_response(exc.message, status_code=404)
    except ValidationError as exc:
        return error_response(exc.message, status_code=422)
    except ServiceUnavailableError as exc:
        return error_response(exc.message, status_code=503)
    except SakshamError as exc:
        return error_response(exc.message, status_code=500)
