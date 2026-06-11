"""Application constants and enums for Saksham AI backend."""

from enum import Enum


class LearningMode(str, Enum):
    """Supported learning mode prompt routing."""

    LEARN = "learn"
    SIMPLIFY = "simplify"
    HINDI = "hindi"
    QUIZ = "quiz"
    SUMMARY = "summary"
    BEGINNER = "beginner"
    DYSLEXIA = "dyslexia"
    VISUAL = "visual"
    LEARN_FROM_SAKSHAM = "learn_from_saksham"
    KEY_CONCEPTS = "key_concepts"
    AUTO_ANALYSIS = "auto_analysis"


class SourceType(str, Enum):
    """RAG source selection."""

    DOCUMENT = "document"
    SAKSHAM = "saksham"


class AccessibilityProfile(str, Enum):
    """Accessibility profile overrides for prompt selection."""

    BEGINNER = "beginner"
    DYSLEXIA = "dyslexia"
    VISUAL = "visual"


class IndexName(str, Enum):
    """FAISS index identifiers."""

    USER = "user_index"
    SAKSHAM = "saksham_index"


# Retrieval defaults
TOP_K = 5
CHUNK_SIZE_TOKENS = 700
CHUNK_OVERLAP_TOKENS = 100

# Upload constraints
MAX_PDF_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
ALLOWED_PDF_EXTENSIONS = {".pdf"}

# Auto-analysis limits
MAX_AUTO_ANALYSIS_TOKENS = 3000
MAX_KEY_CONCEPTS = 10
