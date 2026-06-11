"""API tests for upload endpoint."""

import io

import fitz
import pytest


def _make_pdf_bytes(text: str = "Educational content about photosynthesis and plants.") -> bytes:
    """Create PDF bytes for testing."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def test_upload_rejects_non_pdf(client):
    """Non-PDF files should be rejected."""
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 422
    assert response.json()["success"] is False


def test_upload_rejects_empty_file(client):
    """Empty files should be rejected."""
    response = client.post(
        "/upload",
        files={"file": ("test.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 422


def test_upload_success(client):
    """Valid PDF upload should return document metadata."""
    pdf_bytes = _make_pdf_bytes()
    response = client.post(
        "/upload",
        files={"file": ("chapter1.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "document_id" in data["data"]
    assert "summary" in data["data"]
    assert "key_concepts" in data["data"]


@pytest.mark.integration
def test_upload_integration_real_llm(client):
    """Integration test with real Ollama (skipped by default)."""
    pdf_bytes = _make_pdf_bytes("Force and motion are fundamental concepts in physics.")
    response = client.post(
        "/upload",
        files={"file": ("physics.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 201
