"""Saksham knowledge base browse endpoints."""

import logging

from fastapi import APIRouter, Query

from api.responses import error_response, success_response
from services.knowledge_service import list_chapters, list_classes, list_subjects, list_topics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/saksham", tags=["saksham"])


@router.get("/classes")
def get_classes():
    """List available class levels."""
    classes = list_classes()
    return success_response({"classes": classes})


@router.get("/subjects")
def get_subjects(class_level: int = Query(..., ge=6, le=10)):
    """List subjects for a class level."""
    subjects = list_subjects(class_level)
    if not subjects:
        return error_response(
            f"No subjects found for class {class_level}.",
            status_code=404,
        )
    return success_response({"subjects": subjects})


@router.get("/chapters")
def get_chapters(
    class_level: int = Query(..., ge=6, le=10),
    subject: str = Query(..., min_length=1),
):
    """List curriculum chapters for a class and subject."""
    chapters = list_chapters(class_level, subject)
    if not chapters:
        return error_response(
            f"No chapters found for class {class_level}, subject '{subject}'.",
            status_code=404,
        )
    return success_response({"chapters": chapters})


@router.get("/topics")
def get_topics(
    class_level: int = Query(..., ge=6, le=10),
    subject: str = Query(..., min_length=1),
):
    """List chapter titles (backward-compatible alias for /chapters)."""
    chapters = list_chapters(class_level, subject)
    if not chapters:
        return error_response(
            f"No topics found for class {class_level}, subject '{subject}'.",
            status_code=404,
        )
    return success_response({"topics": [c["chapter_title"] for c in chapters]})
