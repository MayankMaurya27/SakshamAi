"""Unit tests for FAISS manager."""

import numpy as np

from ai.faiss_manager import FaissManager


def test_create_and_search(faiss_manager: FaissManager):
    """Adding vectors and searching should return results."""
    vectors = np.random.randn(5, 384).astype(np.float32)
    metadata = [{"text": f"chunk {i}"} for i in range(5)]
    ids = faiss_manager.add_vectors(vectors, metadata)

    assert len(ids) == 5
    assert faiss_manager.total_vectors == 5

    query = vectors[0]
    results = faiss_manager.search(query, top_k=3)
    assert len(results) <= 3
    assert results[0][0] == ids[0]


def test_search_empty_index(faiss_manager: FaissManager):
    """Empty index should return no results."""
    query = np.random.randn(384).astype(np.float32)
    results = faiss_manager.search(query)
    assert results == []


def test_save_and_load_index(faiss_manager: FaissManager, tmp_path):
    """Index should persist and reload correctly."""
    vectors = np.random.randn(3, 384).astype(np.float32)
    metadata = [{"text": f"chunk {i}"} for i in range(3)]
    faiss_manager.add_vectors(vectors, metadata)

    index_path = tmp_path / "test.faiss"
    meta_path = tmp_path / "test_meta.json"
    faiss_manager.save_index(index_path, meta_path)

    new_manager = FaissManager(name="loaded", dimension=384)
    assert new_manager.load_index(index_path, meta_path)
    assert new_manager.total_vectors == 3
