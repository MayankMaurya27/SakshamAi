"""Integration tests for Saksham knowledge base."""

import pytest

from services.knowledge_service import list_chapters


@pytest.mark.integration
def test_saksham_chapters_api(client):
    """Chapters endpoint should return Class 8 Science chapters."""
    response = client.get(
        "/saksham/chapters",
        params={"class_level": 8, "subject": "Science"},
    )
    assert response.status_code == 200
    chapters = response.json()["data"]["chapters"]
    assert len(chapters) >= 13


@pytest.mark.integration
def test_saksham_ask(client):
    """Ask with saksham source should return an answer from chapter content."""
    chapters = list_chapters(8, "Science")
    assert chapters

    response = client.post(
        "/ask",
        json={
            "question": "What is force?",
            "source": "saksham",
            "class_level": 8,
            "subject": "Science",
            "chapter": "Exploring Forces",
        },
    )
    assert response.status_code == 200
    answer = response.json()["data"]["answer"]
    assert answer
    assert "not found" not in answer.lower()
