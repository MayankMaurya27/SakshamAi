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


def test_delete_document_not_found(client):
    """Deleting a missing document should return 404."""
    response = client.delete("/document/999")
    assert response.status_code == 404


def test_delete_document_success(client, db_session, test_settings, monkeypatch):
    """Deleting a document should remove its stored PDF file."""
    uploads_dir = test_settings.uploads_dir
    uploads_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = uploads_dir / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 test")

    repo = DocumentRepository(db_session)
    doc = repo.create(filename="sample.pdf", filepath=str(pdf_path))

    monkeypatch.setattr("services.document_service.rebuild_user_index", lambda db: None)

    response = client.delete(f"/document/{doc.id}")
    assert response.status_code == 200
    assert response.json()["data"]["deleted"] is True
    assert not pdf_path.exists()
    assert repo.get_by_id(doc.id) is None
