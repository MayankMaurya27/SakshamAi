"""Quiz explanation endpoint — generates rich answer feedback."""

import logging

from fastapi import APIRouter
from pydantic import BaseModel, Field

from api.responses import error_response, success_response
from exceptions import ServiceUnavailableError, SakshamError
from services.quiz_explain_service import generate_quiz_explanation, generate_batch_explanations

logger = logging.getLogger(__name__)
router = APIRouter(tags=["quiz"])


class ExplainRequest(BaseModel):
    """Request body for a single quiz answer explanation."""
    question: str
    options: dict[str, str]
    correct_answer: str
    student_answer: str
    topic: str | None = None
    subject: str | None = None
    class_level: int | None = None


class BatchExplainRequest(BaseModel):
    """Request body for batch quiz explanations."""
    questions: list[dict] = Field(..., min_length=1, max_length=20)
    student_answers: dict[int, str]
    topic: str | None = None
    subject: str | None = None
    class_level: int | None = None


@router.post("/quiz/explain")
def explain_quiz_answer(request: ExplainRequest):
    """Generate a rich explanation for a single quiz answer."""
    try:
        result = generate_quiz_explanation(
            question=request.question,
            options=request.options,
            correct_answer=request.correct_answer,
            student_answer=request.student_answer,
            topic=request.topic,
            subject=request.subject,
            class_level=request.class_level,
        )
        return success_response(result)
    except ServiceUnavailableError as exc:
        return error_response(exc.message, status_code=503)
    except SakshamError as exc:
        return error_response(exc.message, status_code=500)


@router.post("/quiz/explain/batch")
def explain_quiz_batch(request: BatchExplainRequest):
    """Generate explanations for a batch of quiz answers."""
    try:
        results = generate_batch_explanations(
            questions=request.questions,
            student_answers=request.student_answers,
            topic=request.topic,
            subject=request.subject,
            class_level=request.class_level,
        )
        return success_response({"explanations": results})
    except ServiceUnavailableError as exc:
        return error_response(exc.message, status_code=503)
    except SakshamError as exc:
        return error_response(exc.message, status_code=500)
