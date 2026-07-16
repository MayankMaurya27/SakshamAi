"""Pydantic request/response schemas for API endpoints."""

from pydantic import BaseModel, Field, model_validator

from config.constants import AccessibilityProfile, LearningMode, LocalizeContentType, SourceType


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
    include_audio: bool = False


class AskResponse(BaseModel):
    """Response data for POST /ask."""

    answer: str


class SummaryRequest(BaseModel):
    """Request body for POST /summary."""

    source: SourceType = SourceType.DOCUMENT
    document_id: int | None = None
    class_level: int | None = Field(None, ge=6, le=10)
    subject: str | None = None
    chapter: str | None = None
    topic: str | None = None  # backward-compatible alias for chapter
    regenerate: bool = False
    accessibility_profile: AccessibilityProfile | None = None
    include_audio: bool = False


class QuizRequest(BaseModel):
    """Request body for POST /quiz."""

    source: SourceType = SourceType.SAKSHAM
    document_id: int | None = None
    class_level: int | None = Field(None, ge=6, le=10)
    subject: str | None = None
    chapter: str | None = None
    topic: str | None = None  # backward-compatible alias for chapter
    question_count: int = Field(default=10, ge=3, le=15)
    accessibility_profile: AccessibilityProfile | None = None
    include_audio: bool = False


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
    include_audio: bool = False


class AudioRequest(BaseModel):
    """Request body for POST /audio."""

    text: str = Field(..., min_length=1)


class QuizQuestionLocalize(BaseModel):
    """One MCQ for Hinenglish localization."""

    question: str = Field(..., min_length=1)
    option_a: str = Field(..., min_length=1)
    option_b: str = Field(..., min_length=1)
    option_c: str = Field(..., min_length=1)
    option_d: str = Field(..., min_length=1)
    correct_answer: str = Field(..., min_length=1)


class QuizLocalizePayload(BaseModel):
    """Quiz payload for Hinenglish localization."""

    questions: list[QuizQuestionLocalize] = Field(..., min_length=1)


class LocalizeHiRequest(BaseModel):
    """Request body for POST /localize/hi."""

    text: str | None = None
    content_type: LocalizeContentType
    quiz: QuizLocalizePayload | None = None
    class_level: int | None = Field(None, ge=6, le=10)
    subject: str | None = None
    include_audio: bool = False
    preserve_terms: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_payload(self) -> "LocalizeHiRequest":
        if self.content_type == LocalizeContentType.QUIZ:
            if self.quiz is None or not self.quiz.questions:
                raise ValueError("quiz.questions is required when content_type is quiz.")
        elif not self.text or not self.text.strip():
            raise ValueError("text is required when content_type is not quiz.")
        return self
