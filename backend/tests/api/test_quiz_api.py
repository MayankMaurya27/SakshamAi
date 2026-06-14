"""API tests for quiz generation."""

import pytest

from config.constants import SourceType


def test_saksham_quiz_requires_chapter_fields(client):
    """Saksham quiz should validate required chapter fields."""
    response = client.post(
        "/quiz",
        json={
            "source": SourceType.SAKSHAM.value,
            "question_count": 5,
        },
    )
    assert response.status_code == 422


def test_document_quiz_requires_document_id(client, db_session):
    """Document quiz should require document_id."""
    response = client.post(
        "/quiz",
        json={
            "source": SourceType.DOCUMENT.value,
            "question_count": 5,
        },
    )
    assert response.status_code == 422


def test_saksham_quiz_returns_questions(client, monkeypatch):
    """Saksham quiz should return normalized MCQs."""
    monkeypatch.setattr(
        "services.quiz_service.validate_saksham_chapter",
        lambda class_level, subject, chapter_ref: {
            "chapter_id": "agriculture",
            "chapter_title": "Agriculture",
        },
    )
    monkeypatch.setattr(
        "services.quiz_service.get_chapter_chunk_texts",
        lambda class_level, subject, chapter_ref: [
            "Agriculture is an primary activity that provides food and raw materials across India.",
            "Rice and wheat are major crops grown in different seasons across many states.",
        ],
    )
    monkeypatch.setattr("services.quiz_service.load_cached_quiz", lambda path: None)
    monkeypatch.setattr("services.quiz_service.save_cached_quiz", lambda path, payload: None)

    response = client.post(
        "/quiz",
        json={
            "source": SourceType.SAKSHAM.value,
            "class_level": 10,
            "subject": "Geography",
            "chapter": "Agriculture",
            "question_count": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["source"] == SourceType.SAKSHAM.value
    assert len(data["questions"]) == 5
    assert data["questions"][0]["options"]["A"]
