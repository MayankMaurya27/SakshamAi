"""Integration tests for upload flow."""

import io

import fitz
import pytest

from database.repositories import DocumentRepository, QuizRepository


def _make_pdf_bytes(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


@pytest.mark.integration
def test_upload_to_query_flow(client, db_session):
    """Upload PDF then query it via /ask."""
    pdf_bytes = _make_pdf_bytes(
        "Photosynthesis is the process by which green plants make food using sunlight."
    )
    upload_resp = client.post(
        "/upload",
        files={"file": ("bio.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload_resp.status_code == 201
    doc_id = upload_resp.json()["data"]["document_id"]

    ask_resp = client.post(
        "/ask",
        json={
            "question": "What is photosynthesis?",
            "source": "document",
            "document_id": doc_id,
        },
    )
    assert ask_resp.status_code == 200
    assert ask_resp.json()["data"]["answer"]


@pytest.mark.integration
def test_upload_summary_quiz(client, db_session):
    """Upload should store summary and quiz retrievable via endpoints."""
    pdf_bytes = _make_pdf_bytes("Force is a push or pull. Newton studied force and motion.")
    upload_resp = client.post(
        "/upload",
        files={"file": ("force.pdf", pdf_bytes, "application/pdf")},
    )
    doc_id = upload_resp.json()["data"]["document_id"]

    summary_resp = client.post(
        "/summary",
        json={"source": "document", "document_id": doc_id},
    )
    assert summary_resp.status_code == 200
    assert summary_resp.json()["data"]["summary"]

    quiz_resp = client.post(
        "/quiz",
        json={
            "source": "document",
            "document_id": doc_id,
            "question_count": 5,
        },
    )
    assert quiz_resp.status_code == 200
    assert len(quiz_resp.json()["data"]["questions"]) == 5

    doc_resp = client.get(f"/document/{doc_id}")
    assert doc_resp.status_code == 200
