"""Custom application exceptions."""


class SakshamError(Exception):
    """Base exception for Saksham AI backend."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class DocumentNotFoundError(SakshamError):
    """Raised when a document ID does not exist."""


class PDFProcessingError(SakshamError):
    """Raised when PDF extraction or validation fails."""


class ServiceUnavailableError(SakshamError):
    """Raised when an external local service (Ollama, Piper) is unavailable."""


class IndexNotFoundError(SakshamError):
    """Raised when a required FAISS index is missing."""


class ValidationError(SakshamError):
    """Raised for business validation failures."""
