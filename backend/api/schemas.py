"""Pydantic request/response schemas for API endpoints."""

from pydantic import BaseModel, Field

from config.constants import AccessibilityProfile, LearningMode, SourceType


class AskRequest(BaseModel):
    """Request body for POST /ask."""

    question: str = Field(..., min_length=1)
    source: SourceType = SourceType.DOCUMENT
    document_id: int | None = None
    class_level: int | None = Field(None, ge=6, le=10)
    subject: str | None = None
    chapter: str | None = None
    topic: str | None = None  # backward-compatible alias for chapter
    mode: LearningMode = LearningMode.LEARN
    accessibility_profile: AccessibilityProfile | None = None


class AskResponse(BaseModel):
    """Response data for POST /ask."""

    answer: str


class SummaryRequest(BaseModel):
    """Request body for POST /summary."""

    document_id: int
    regenerate: bool = False


class QuizRequest(BaseModel):
    """Request body for POST /quiz."""

    document_id: int
    regenerate: bool = False


class LearningModeRequest(BaseModel):
    """Shared request for simplify and hindi endpoints."""

    question: str = Field(..., min_length=1)
    source: SourceType = SourceType.DOCUMENT
    document_id: int | None = None
    class_level: int | None = Field(None, ge=6, le=10)
    subject: str | None = None
    chapter: str | None = None
    topic: str | None = None  # backward-compatible alias for chapter
    accessibility_profile: AccessibilityProfile | None = None


class AudioRequest(BaseModel):
    """Request body for POST /audio."""

    text: str = Field(..., min_length=1)
