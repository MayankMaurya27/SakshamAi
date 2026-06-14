"""FAISS vector index management."""

import json
import logging
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class FaissManager:
    """Manage a single FAISS index with ID metadata mapping."""

    def __init__(self, name: str, dimension: int = 384) -> None:
        self.name = name
        self.dimension = dimension
        self.index: faiss.IndexFlatIP | None = None
        self.id_map: dict[int, dict[str, Any]] = {}
        self._next_id = 0

    def create_index(self) -> None:
        """Create a new empty FAISS index."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_map = {}
        self._next_id = 0
        logger.info("Created FAISS index '%s' with dimension %d", self.name, self.dimension)

    def _ensure_index(self) -> faiss.IndexFlatIP:
        if self.index is None:
            self.create_index()
        assert self.index is not None
        return self.index

    def add_vectors(
        self,
        vectors: np.ndarray,
        metadata_list: list[dict[str, Any]],
    ) -> list[int]:
        """Add vectors with metadata and return assigned FAISS IDs."""
        if len(vectors) == 0:
            return []

        index = self._ensure_index()
        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)

        faiss.normalize_L2(vectors)
        index.add(vectors)

        assigned_ids: list[int] = []
        for meta in metadata_list:
            faiss_id = self._next_id
            self._next_id += 1
            self.id_map[faiss_id] = meta
            assigned_ids.append(faiss_id)

        logger.info("Added %d vectors to index '%s'", len(assigned_ids), self.name)
        return assigned_ids

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int | None = None,
    ) -> list[tuple[int, float, dict[str, Any]]]:
        """Search index and return (faiss_id, score, metadata) tuples."""
        if self.index is None or self.index.ntotal == 0:
            return []

        k = top_k or settings.top_k
        k = min(k, self.index.ntotal)

        query = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
        faiss.normalize_L2(query)

        scores, indices = self.index.search(query, k)
        results: list[tuple[int, float, dict[str, Any]]] = []

        for idx, score in zip(indices[0], scores[0]):
            if idx == -1:
                continue
            faiss_id = int(idx)
            meta = self.id_map.get(faiss_id, {})
            results.append((faiss_id, float(score), meta))

        return results

    def search_filtered(
        self,
        query_vector: np.ndarray,
        filter_fn,
        top_k: int | None = None,
    ) -> list[tuple[int, float, dict[str, Any]]]:
        """Search only vectors whose metadata passes filter_fn."""
        if self.index is None or self.index.ntotal == 0:
            return []

        k = top_k or settings.top_k
        query = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
        faiss.normalize_L2(query)
        query_flat = query[0]

        scored: list[tuple[float, int, dict[str, Any]]] = []
        for faiss_id, meta in self.id_map.items():
            if not filter_fn(meta):
                continue
            vector = self.index.reconstruct(faiss_id)
            score = float(np.dot(query_flat, vector))
            scored.append((score, faiss_id, meta))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            (faiss_id, score, meta)
            for score, faiss_id, meta in scored[:k]
        ]

    def save_index(self, index_path: Path, meta_path: Path) -> None:
        """Persist index and metadata to disk."""
        index = self._ensure_index()
        index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(index_path))

        meta = {
            "next_id": self._next_id,
            "id_map": {str(k): v for k, v in self.id_map.items()},
        }
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        logger.info("Saved FAISS index '%s' to %s", self.name, index_path)

    def load_index(self, index_path: Path, meta_path: Path) -> bool:
        """Load index and metadata from disk. Returns True if successful."""
        if not index_path.exists() or not meta_path.exists():
            return False

        self.index = faiss.read_index(str(index_path))
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self._next_id = meta.get("next_id", 0)
        self.id_map = {int(k): v for k, v in meta.get("id_map", {}).items()}
        logger.info(
            "Loaded FAISS index '%s' with %d vectors from %s",
            self.name,
            self.index.ntotal,
            index_path,
        )
        return True

    @property
    def total_vectors(self) -> int:
        """Return number of vectors in the index."""
        if self.index is None:
            return 0
        return self.index.ntotal


_user_index: FaissManager | None = None
_saksham_index: FaissManager | None = None


def get_user_index() -> FaissManager:
    """Return singleton user document FAISS index."""
    global _user_index
    if _user_index is None:
        _user_index = FaissManager(name="user_index")
        if not _user_index.load_index(settings.user_index_path, settings.user_index_meta_path):
            _user_index.create_index()
    return _user_index


def get_saksham_index() -> FaissManager:
    """Return singleton Saksham knowledge base FAISS index."""
    global _saksham_index
    if _saksham_index is None:
        _saksham_index = FaissManager(name="saksham_index")
        if not _saksham_index.load_index(
            settings.saksham_index_path, settings.saksham_index_meta_path
        ):
            _saksham_index.create_index()
    return _saksham_index


def save_user_index() -> None:
    """Persist user index to disk."""
    if _user_index is not None:
        _user_index.save_index(settings.user_index_path, settings.user_index_meta_path)


def reset_user_index() -> FaissManager:
    """Replace the user index with a fresh empty index and persist it."""
    global _user_index
    _user_index = FaissManager(name="user_index")
    _user_index.create_index()
    return _user_index


def save_saksham_index() -> None:
    """Persist Saksham index to disk."""
    if _saksham_index is not None:
        _saksham_index.save_index(
            settings.saksham_index_path, settings.saksham_index_meta_path
        )


def reset_saksham_index() -> None:
    """Reset saksham index singleton (for rebuild)."""
    global _saksham_index
    _saksham_index = None


def reset_indexes_for_testing() -> None:
    """Reset singleton indexes (for testing)."""
    global _user_index, _saksham_index
    _user_index = None
    _saksham_index = None
    from ai.bm25_store import reset_bm25_store_for_testing
    from ai.reranker import reset_reranker_for_testing

    reset_bm25_store_for_testing()
    reset_reranker_for_testing()
