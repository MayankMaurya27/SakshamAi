"""API tests for document endpoints."""

from database.repositories import DocumentRepository


def test_list_documents_empty(client):
    """Empty document list should return success."""
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["documents"] == []


def test_get_document_not_found(client):
    """Missing document should return 404."""
    response = client.get("/document/999")
    assert response.status_code == 404
    assert response.json()["success"] is False


def test_get_document_success(client, db_session):
    """Existing document should return details with quizzes."""
    repo = DocumentRepository(db_session)
    doc = repo.create(
        filename="science.pdf",
        filepath="/uploads/science.pdf",
        summary="Science chapter summary",
        key_concepts=[{"name": "Force", "description": "Push or pull"}],
    )

    response = client.get(f"/document/{doc.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["filename"] == "science.pdf"
    assert data["data"]["summary"] == "Science chapter summary"
