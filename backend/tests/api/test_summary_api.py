"""API tests for summary generation."""

from config.constants import SourceType
from services.summary_parser import count_paragraphs


def test_document_summary_requires_document_id(client):
    response = client.post(
        "/summary",
        json={"source": SourceType.DOCUMENT.value},
    )
    assert response.status_code == 422


def test_saksham_summary_requires_chapter_fields(client):
    response = client.post(
        "/summary",
        json={"source": SourceType.SAKSHAM.value},
    )
    assert response.status_code == 422


def test_saksham_summary_returns_prose_payload(client, monkeypatch):
    monkeypatch.setattr(
        "services.summary_service.validate_saksham_chapter",
        lambda class_level, subject, chapter_ref: {
            "chapter_id": "electricity",
            "chapter_title": "Electricity",
        },
    )
    monkeypatch.setattr(
        "services.summary_service.get_chapter_chunk_texts",
        lambda class_level, subject, chapter_ref: [
            "A continuous and closed path of an electric current is called an electric circuit.",
            "A component used to regulate current without changing the voltage source is called variable resistance.",
            "A conductor having some appreciable resistance is called a resistor.",
        ],
    )
    monkeypatch.setattr("services.summary_service.load_cached_summary", lambda path: None)
    monkeypatch.setattr("services.summary_service.save_cached_summary", lambda path, payload: None)

    response = client.post(
        "/summary",
        json={
            "source": SourceType.SAKSHAM.value,
            "class_level": 10,
            "subject": "Science",
            "chapter": "Electricity",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["chapter_id"] == "electricity"
    assert data["summary"]
    assert count_paragraphs(data["summary"]) >= 2
    assert data["format_version"] == "v2-prose"
    assert "overview" not in data
    assert "key_concepts" not in data
