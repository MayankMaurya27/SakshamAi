"""PDF text extraction using PyMuPDF."""

import logging
import re

import fitz

from exceptions import PDFProcessingError

logger = logging.getLogger(__name__)


def _clean_text(text: str) -> str:
    """Normalize whitespace and strip common PDF artifacts."""
    # Remove null bytes
    text = text.replace("\x00", "")

    # Remove common NCERT/textbook page headers and footers
    text = re.sub(
        r"(?im)^\s*(?:NCERT|not to be republished|©\s*NCERT|free distribution|"
        r"downloaded from|www\.\S+|https?://\S+|"
        r"Rationalised \d{4}-\d{2}|"
        r"\d{4}-\d{2}\s*$)",
        "",
        text,
    )

    # Remove repeated page numbers (standalone numbers on their own line)
    text = re.sub(r"(?m)^\s*\d{1,3}\s*$", "", text)

    # Remove figure/image captions like "Fig. 1.2: ...", "Figure 3 ..."
    text = re.sub(r"(?i)(?:Fig(?:ure)?\.?\s*\d+[\.\d]*\s*:?\s*[^\n]{0,80})", "", text)

    # Normalize common Unicode characters
    replacements = {
        "\u2018": "'", "\u2019": "'",  # smart quotes
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",  # dashes
        "\u2026": "...",  # ellipsis
        "\u00a0": " ",  # non-breaking space
        "\ufeff": "",  # BOM
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Clean OCR artifacts: isolated single characters, excessive punctuation
    text = re.sub(r"(?m)^\s*[a-zA-Z]\s*$", "", text)  # lone letters on a line
    text = re.sub(r"[•·■□▪▸►▶]{2,}", "", text)  # repeated bullet symbols

    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalize remaining whitespace within lines
    text = re.sub(r"[ \t]+", " ", text)

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
