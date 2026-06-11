"""Integration tests for learning modes."""

import pytest


@pytest.mark.integration
def test_simplify_mode(client):
    """Simplify endpoint should return simplified answer."""
    response = client.post(
        "/simplify",
        json={
            "question": "What is force?",
            "source": "saksham",
            "class_level": 8,
            "subject": "Science",
            "topic": "Force and Pressure",
        },
    )
    assert response.status_code == 200
    assert "simplified_answer" in response.json()["data"]


@pytest.mark.integration
def test_hindi_mode(client):
    """Hindi endpoint should return Hindi answer."""
    response = client.post(
        "/hindi",
        json={
            "question": "What is force?",
            "source": "saksham",
            "class_level": 8,
            "subject": "Science",
            "topic": "Force and Pressure",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["answer"]


def test_health_check(client):
    """Health endpoint should return healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["success"] is True
