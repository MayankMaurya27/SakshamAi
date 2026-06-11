"""Quiz generation endpoint."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.responses import error_response, success_response
from api.schemas import QuizRequest
from database.db import get_db
from exceptions import DocumentNotFoundError, SakshamError, ServiceUnavailableError
from services.quiz_service import get_quiz

logger = logging.getLogger(__name__)
router = APIRouter(tags=["quiz"])


@router.post("/quiz")
def generate_quiz(
    request: QuizRequest,
    db: Session = Depends(get_db),
):
    """Get or regenerate document quiz."""
    try:
        result = get_quiz(request.document_id, db, regenerate=request.regenerate)
        return success_response(result)
    except DocumentNotFoundError as exc:
        return error_response(exc.message, status_code=404)
    except ServiceUnavailableError as exc:
        return error_response(exc.message, status_code=503)
    except SakshamError as exc:
        return error_response(exc.message, status_code=500)
