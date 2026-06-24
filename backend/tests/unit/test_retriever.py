"""Unit tests for retrieval helpers."""

from ai.retriever import get_search_terms


def test_search_terms_include_content_phrases_for_electricity_question():
    terms = get_search_terms(
        "How did the spread of electricity help farmers in Palampur?"
    )
    lowered = [term.lower() for term in terms]
    assert "palampur" in lowered
    assert any("electricity" in term for term in lowered)


def test_search_terms_include_minimum_wages_phrase():
    terms = get_search_terms(
        "Why are the wages for farm labourers in Palampur less than minimum wages?"
    )
    lowered = [term.lower() for term in terms]
    assert "minimum wages" in lowered or "farm labourers" in lowered


def test_retrieve_document_context_hybrid(db_session, monkeypatch):
    """Document retrieval should use hybrid (semantic + BM25) flow when enabled."""
    import numpy as np
    from ai.embeddings import MockEmbeddings, set_embedding_model
    from ai.faiss_manager import FaissManager, reset_indexes_for_testing
    from ai import faiss_manager
    from ai.retriever import retrieve_document_context
    from database.repositories import ChunkRepository, DocumentRepository

    reset_indexes_for_testing()
    set_embedding_model(MockEmbeddings(dimension=384))

    manager = FaissManager(name="user_index", dimension=384)
    manager.create_index()

    # Stub get_user_index to return our manager
    monkeypatch.setattr("ai.retriever.get_user_index", lambda: manager)
    faiss_manager._user_index = manager

    # Create dummy document and chunk records
    doc_repo = DocumentRepository(db_session)
    doc = doc_repo.create(filename="doc.pdf", filepath="/uploads/doc.pdf")

    text1 = "Educational content about photosynthesis and how green plants make food. Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy."
    text2 = "Newton's laws of motion are three physical laws that, together, laid the foundation for classical mechanics. They describe the relationship between a body and the forces acting upon it."

    v1 = np.random.randn(384).astype(np.float32)
    v2 = np.random.randn(384).astype(np.float32)
    
    # Normalize vectors so cosine similarity works nicely
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)

    def mock_embed_text(text: str, is_query: bool = False) -> np.ndarray:
        if "photosynthesis" in text.lower():
            return v1
        return v2

    monkeypatch.setattr("ai.retriever.embed_text", mock_embed_text)

    batch = np.vstack([v1, v2])

    faiss_ids = manager.add_vectors(
        batch,
        [
            {"source": "user_document", "document_id": doc.id, "chunk_text": text1, "chunk_index": 0},
            {"source": "user_document", "document_id": doc.id, "chunk_text": text2, "chunk_index": 1},
        ],
    )

    chunk_repo = ChunkRepository(db_session)
    chunk_repo.create_batch(
        doc.id,
        [
            (0, text1, faiss_ids[0]),
            (1, text2, faiss_ids[1]),
        ],
    )

    # Perform retrieval
    contexts = retrieve_document_context(
        "What is photosynthesis?",
        db=db_session,
        document_id=doc.id,
    )

    assert len(contexts) > 0
    # The first context should match photosynthesis
    assert "photosynthesis" in contexts[0].text.lower()
    # The match type should be 'hybrid'
    assert contexts[0].metadata.get("match_type") == "hybrid"

    reset_indexes_for_testing()
