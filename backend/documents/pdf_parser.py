"""PDF text extraction using PyMuPDF."""

import logging
import re

import fitz

from exceptions import PDFProcessingError

logger = logging.getLogger(__name__)


def _clean_text(text: str) -> str:
    """Normalize whitespace in extracted text."""
    text = text.replace("\x00", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text(filepath: str) -> tuple[str, int]:
    """
    Extract text from a PDF file.

    Returns:
        Tuple of (cleaned_text, page_count).

    Raises:
        PDFProcessingError: If the PDF is empty or corrupted.
    """
    try:
        doc = fitz.open(filepath)
    except Exception as exc:
        logger.error("Failed to open PDF: %s", filepath)
        raise PDFProcessingError(f"Corrupted or invalid PDF file: {exc}") from exc

    try:
        page_count = doc.page_count
        if page_count == 0:
            raise PDFProcessingError("PDF contains no pages.")

        pages: list[str] = []
        for page_num in range(page_count):
            page = doc.load_page(page_num)
            pages.append(page.get_text())

        full_text = _clean_text("\n".join(pages))
        if not full_text:
            raise PDFProcessingError("PDF contains no extractable text.")

        logger.info("Extracted text from PDF: %s (%d pages)", filepath, page_count)
        return full_text, page_count
    finally:
        doc.close()
