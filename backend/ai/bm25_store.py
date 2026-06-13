"""BM25 lexical index for Saksham curriculum chapters (built at ingest, loaded offline)."""

from __future__ import annotations

import json
import logging
import re
from functools import lru_cache
from typing import Any

from rank_bm25 import BM25Okapi

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+", re.I)
INDEX_VERSION = 1


def chapter_storage_key(class_level: int, subject: str, chapter_id: str) -> str:
    """Stable key for a chapter in the BM25 sidecar file."""
    return f"{class_level}|{subject.lower()}|{chapter_id.lower()}"


def tokenize(text: str) -> list[str]:
    """Tokenize text for BM25 (lowercase alphanumeric tokens)."""
    return _TOKEN_PATTERN.findall(text.lower())


class ChapterBM25:
    """In-memory BM25 index for one chapter's chunks."""

    def __init__(
        self,
        faiss_ids: list[int],
        documents: list[str],
        tokenized_corpus: list[list[str]] | None = None,
    ) -> None:
        self.faiss_ids = faiss_ids
        self.documents = documents
        corpus = tokenized_corpus or [tokenize(doc) for doc in documents]
        self._bm25 = BM25Okapi(corpus)

    def search(self, query: str, top_k: int) -> list[tuple[int, float, str]]:
        """Return (faiss_id, score, text) for top matching chunks."""
        if not self.documents or not query.strip():
            return []

        tokens = tokenize(query)
        if not tokens:
            return []

        scores = self._bm25.get_scores(tokens)
        ranked = sorted(
            enumerate(scores),
            key=lambda item: item[1],
            reverse=True,
        )

        results: list[tuple[int, float, str]] = []
        for doc_idx, score in ranked[:top_k]:
            if score <= 0:
                break
            results.append(
                (self.faiss_ids[doc_idx], float(score), self.documents[doc_idx])
            )
        return results


class SakshamBM25Store:
    """Load and query pre-built BM25 indexes per chapter."""

    def __init__(self, index_path=None) -> None:
        self.index_path = index_path or settings.saksham_bm25_index_path
        self._chapters: dict[str, ChapterBM25] = {}
        self._loaded = False

    def load(self) -> bool:
        """Load BM25 sidecar from disk. Returns True if loaded."""
        if self._loaded:
            return bool(self._chapters)

        if not self.index_path.exists():
            logger.info("BM25 sidecar not found at %s", self.index_path)
            self._loaded = True
            return False

        raw = json.loads(self.index_path.read_text(encoding="utf-8"))
        if raw.get("version") != INDEX_VERSION:
            logger.warning("BM25 index version mismatch; ignoring sidecar")
            self._loaded = True
            return False

        for key, payload in raw.get("chapters", {}).items():
            faiss_ids = payload.get("faiss_ids", [])
            documents = payload.get("documents", [])
            tokenized = payload.get("tokenized_corpus")
            if not faiss_ids or not documents:
                continue
            self._chapters[key] = ChapterBM25(faiss_ids, documents, tokenized)

        self._loaded = True
        logger.info("Loaded BM25 index for %d chapters from %s", len(self._chapters), self.index_path)
        return bool(self._chapters)

    def search_chapter(
        self,
        class_level: int,
        subject: str,
        chapter_id: str,
        query: str,
        top_k: int,
    ) -> list[tuple[int, float, str]]:
        """BM25 search within one chapter."""
        if not self._loaded:
            self.load()

        key = chapter_storage_key(class_level, subject, chapter_id)
        chapter = self._chapters.get(key)
        if chapter is None:
            return []
        return chapter.search(query, top_k)

    @staticmethod
    def build_from_faiss_metadata(id_map: dict[int, dict[str, Any]]) -> dict[str, Any]:
        """Build serializable BM25 sidecar from FAISS id_map after ingest."""
        grouped: dict[str, dict[str, list]] = {}

        for faiss_id, meta in id_map.items():
            chapter_id = meta.get("chapter_id")
            class_level = meta.get("class")
            subject = meta.get("subject")
            text = meta.get("chunk_text", "")
            if chapter_id is None or class_level is None or not subject or not text:
                continue

            key = chapter_storage_key(int(class_level), str(subject), str(chapter_id))
            bucket = grouped.setdefault(key, {"faiss_ids": [], "documents": []})
            bucket["faiss_ids"].append(faiss_id)
            bucket["documents"].append(text)

        chapters: dict[str, Any] = {}
        for key, bucket in grouped.items():
            # Sort by faiss_id (ingest order ≈ chunk order)
            pairs = sorted(zip(bucket["faiss_ids"], bucket["documents"]), key=lambda p: p[0])
            faiss_ids = [p[0] for p in pairs]
            documents = [p[1] for p in pairs]
            tokenized_corpus = [tokenize(doc) for doc in documents]
            chapters[key] = {
                "faiss_ids": faiss_ids,
                "documents": documents,
                "tokenized_corpus": tokenized_corpus,
            }

        return {"version": INDEX_VERSION, "chapters": chapters}

    def save(self, payload: dict[str, Any]) -> None:
        """Persist BM25 sidecar to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_path.write_text(
            json.dumps(payload, ensure_ascii=False),
            encoding="utf-8",
        )
        self._chapters.clear()
        self._loaded = False
        self.load()
        logger.info("Saved BM25 sidecar with %d chapters", len(payload.get("chapters", {})))


@lru_cache(maxsize=1)
def get_bm25_store() -> SakshamBM25Store:
    """Return singleton BM25 store."""
    return SakshamBM25Store()


def reset_bm25_store_for_testing() -> None:
    """Clear cached BM25 store (tests)."""
    get_bm25_store.cache_clear()
