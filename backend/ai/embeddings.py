"""Embedding generation using multilingual-e5-small."""

import logging
import os
import time
from pathlib import Path
from typing import Protocol

import numpy as np

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

if settings.embedding_local_files_only:
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")


class EmbeddingModel(Protocol):
    """Protocol for embedding model implementations."""

    def embed_text(self, text: str, is_query: bool = False) -> np.ndarray:
        """Embed a single text string."""

    def embed_batch(self, texts: list[str], is_query: bool = False) -> np.ndarray:
        """Embed a batch of text strings."""


class SentenceTransformerEmbeddings:
    """Production embedding model using sentence-transformers."""

    def __init__(
        self,
        model_name: str | None = None,
        local_files_only: bool | None = None,
    ) -> None:
        self.model_name = model_name or settings.embedding_model
        self.local_files_only = (
            local_files_only
            if local_files_only is not None
            else settings.embedding_local_files_only
        )
        self._model = None
        self._resolved_path: str | None = None

    def _resolve_model_path(self) -> str:
        """Resolve model to a local directory path for offline-safe loading."""
        if self._resolved_path is not None:
            return self._resolved_path

        if settings.embedding_model_path is not None:
            path = Path(settings.embedding_model_path)
            if not path.is_dir():
                raise FileNotFoundError(
                    f"embedding_model_path does not exist: {path}"
                )
            self._resolved_path = str(path)
            return self._resolved_path

        if self.local_files_only:
            from huggingface_hub import snapshot_download

            self._resolved_path = snapshot_download(
                self.model_name,
                local_files_only=True,
            )
            return self._resolved_path

        self._resolved_path = self.model_name
        return self._resolved_path

    def _load_model(self) -> None:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            model_path = self._resolve_model_path()
            start = time.time()
            self._model = SentenceTransformer(
                model_path,
                local_files_only=self.local_files_only,
            )
            logger.info(
                "Loaded embedding model from '%s' in %.2fs (local_files_only=%s)",
                model_path,
                time.time() - start,
                self.local_files_only,
            )

    def _prefix(self, text: str, is_query: bool) -> str:
        prefix = "query: " if is_query else "passage: "
        return f"{prefix}{text}"

    def embed_text(self, text: str, is_query: bool = False) -> np.ndarray:
        """Generate embedding for a single text."""
        self._load_model()
        prefixed = self._prefix(text, is_query)
        vector = self._model.encode(prefixed, normalize_embeddings=True)
        return np.array(vector, dtype=np.float32)

    def embed_batch(self, texts: list[str], is_query: bool = False) -> np.ndarray:
        """Generate embeddings for a batch of texts."""
        if not texts:
            return np.array([], dtype=np.float32)
        self._load_model()
        prefixed = [self._prefix(text, is_query) for text in texts]
        vectors = self._model.encode(prefixed, normalize_embeddings=True)
        return np.array(vectors, dtype=np.float32)


class MockEmbeddings:
    """Deterministic mock embeddings for testing."""

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    def _hash_vector(self, text: str) -> np.ndarray:
        rng = np.random.default_rng(abs(hash(text)) % (2**32))
        vector = rng.standard_normal(self.dimension).astype(np.float32)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector

    def embed_text(self, text: str, is_query: bool = False) -> np.ndarray:
        """Return deterministic pseudo-random embedding."""
        return self._hash_vector(text)

    def embed_batch(self, texts: list[str], is_query: bool = False) -> np.ndarray:
        """Return deterministic embeddings for a batch."""
        if not texts:
            return np.array([], dtype=np.float32)
        return np.vstack([self._hash_vector(text) for text in texts])


_embedding_instance: EmbeddingModel | None = None


def get_embedding_model(use_mock: bool = False) -> EmbeddingModel:
    """Return singleton embedding model instance."""
    global _embedding_instance
    if _embedding_instance is None:
        if use_mock:
            _embedding_instance = MockEmbeddings()
        else:
            _embedding_instance = SentenceTransformerEmbeddings()
    return _embedding_instance


def set_embedding_model(model: EmbeddingModel) -> None:
    """Override embedding model (for testing)."""
    global _embedding_instance
    _embedding_instance = model


def preload_embedding_model() -> None:
    """Load embedding model at startup to avoid delay on first request."""
    if not settings.preload_embedding_model:
        return
    logger.info("Preloading embedding model...")
    get_embedding_model().embed_text("warmup", is_query=True)
    logger.info("Embedding model ready")


def embed_text(text: str, is_query: bool = False) -> np.ndarray:
    """Embed a single text using the default model."""
    return get_embedding_model().embed_text(text, is_query=is_query)


def embed_batch(texts: list[str], is_query: bool = False) -> np.ndarray:
    """Embed a batch of texts using the default model."""
    return get_embedding_model().embed_batch(texts, is_query=is_query)
