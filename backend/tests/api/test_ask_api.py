"""API tests for ask endpoint."""

import numpy as np

from ai.faiss_manager import get_user_index, save_user_index
from ai.faiss_manager import reset_indexes_for_testing
from database.repositories import ChunkRepository, DocumentRepository


def test_ask_empty_question(client):
    """Empty question should return 422."""
    response = client.post("/ask", json={"question": "", "source": "document"})
    assert response.status_code == 422


def test_ask_document_not_found(client):
    """Non-existent document_id should return 404."""
    response = client.post(
        "/ask",
        json={"question": "What is force?", "source": "document", "document_id": 999},
    )
    assert response.status_code == 404


def test_ask_saksham_missing_params(client):
    """Saksham source without class/subject/chapter should return 422."""
    response = client.post(
        "/ask",
        json={"question": "What is force?", "source": "saksham"},
    )
    assert response.status_code == 422


def test_ask_with_retrieved_context(client, db_session, monkeypatch):
    """Ask should return answer when context is available."""
    reset_indexes_for_testing()
    monkeypatch.setattr("ai.retriever.get_user_index", get_user_index)

    doc_repo = DocumentRepository(db_session)
    doc = doc_repo.create(filename="test.pdf", filepath="/uploads/test.pdf")

    user_index = get_user_index()
    vectors = np.random.randn(1, 384).astype(np.float32)
    faiss_ids = user_index.add_vectors(
        vectors, [{"chunk_text": "Force is a push or pull on an object.", "chunk_index": 0}]
    )
    ChunkRepository(db_session).create_batch(doc.id, [(0, "Force is a push or pull.", faiss_ids[0])])

    response = client.post(
        "/ask",
        json={
            "question": "What is force?",
            "source": "document",
            "document_id": doc.id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "answer" in data["data"]
