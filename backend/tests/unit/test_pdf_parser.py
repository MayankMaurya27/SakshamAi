"""Unit tests for PDF parser."""

import tempfile
from pathlib import Path

import fitz
import pytest

from documents.pdf_parser import extract_text
from exceptions import PDFProcessingError


def _create_test_pdf(text: str) -> str:
    """Create a temporary PDF with given text."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    doc.save(tmp.name)
    doc.close()
    return tmp.name


def test_extract_text_success():
    """Valid PDF should return extracted text."""
    path = _create_test_pdf("Photosynthesis is the process plants use to make food.")
    try:
        text, page_count = extract_text(path)
        assert "Photosynthesis" in text
        assert page_count == 1
    finally:
        Path(path).unlink(missing_ok=True)


def test_extract_text_empty_pdf():
    """PDF with no text should raise PDFProcessingError."""
    doc = fitz.open()
    doc.new_page()
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    doc.save(tmp.name)
    doc.close()

    try:
        with pytest.raises(PDFProcessingError, match="no extractable text"):
            extract_text(tmp.name)
    finally:
        Path(tmp.name).unlink(missing_ok=True)


def test_extract_text_corrupted_file():
    """Invalid file should raise PDFProcessingError."""
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.write(b"not a pdf")
    tmp.close()
    try:
        with pytest.raises(PDFProcessingError):
            extract_text(tmp.name)
    finally:
        Path(tmp.name).unlink(missing_ok=True)
