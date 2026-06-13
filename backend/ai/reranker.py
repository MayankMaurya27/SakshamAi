"""Optional cross-encoder reranker for Saksham retrieval (lazy-loaded, Jetson-safe)."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Protocol

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class Reranker(Protocol):
    """Protocol for reranking candidate passages."""

    def rerank(
        self,
        query: str,
        candidates: list[tuple[int, str]],
        top_k: int,
    ) -> list[tuple[int, float, str]]:
        """Return (faiss_id, score, text) sorted by relevance."""


class CrossEncoderReranker:
    """Lazy-loaded sentence-transformers CrossEncoder reranker."""

    def __init__(
        self,
        model_name: str | None = None,
        model_path: str | None = None,
        local_files_only: bool | None = None,
    ) -> None:
        self.model_name = model_name or settings.rerank_model
        self.model_path = model_path or (
            str(settings.rerank_model_path) if settings.rerank_model_path else None
        )
        self.local_files_only = (
            local_files_only
            if local_files_only is not None
            else settings.rerank_local_files_only
        )
        self._model = None
        self._load_failed = False

    def _load_model(self):
        if self._model is not None:
            return self._model
        if self._load_failed:
            return None

        try:
            from sentence_transformers import CrossEncoder

            source = self.model_path or self.model_name
            logger.info("Loading reranker model from '%s' (lazy)", source)
            self._model = CrossEncoder(
                source,
                local_files_only=self.local_files_only,
            )
            return self._model
        except OSError as exc:
            logger.warning(
                "Reranker model unavailable (%s); continuing without reranking",
                exc,
            )
            self._load_failed = True
            return None

    def rerank(
        self,
        query: str,
        candidates: list[tuple[int, str]],
        top_k: int,
    ) -> list[tuple[int, float, str]]:
        if not candidates:
            return []

        model = self._load_model()
        if model is None:
            return NoOpReranker().rerank(query, candidates, top_k)

        pairs = [[query, text] for _, text in candidates]
        scores = model.predict(pairs)

        ranked = sorted(
            zip(candidates, scores),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        return [
            (faiss_id, float(score), text)
            for (faiss_id, text), score in ranked[:top_k]
        ]


class NoOpReranker:
    """Passthrough when reranking is disabled."""

    def rerank(
        self,
        query: str,
        candidates: list[tuple[int, str]],
        top_k: int,
    ) -> list[tuple[int, float, str]]:
        return [(faiss_id, 1.0, text) for faiss_id, text in candidates[:top_k]]


@lru_cache(maxsize=1)
def get_reranker() -> Reranker:
    """Return configured reranker singleton."""
    if not settings.rerank_enabled:
        return NoOpReranker()
    return CrossEncoderReranker()


def reset_reranker_for_testing() -> None:
    """Clear cached reranker (tests)."""
    get_reranker.cache_clear()
