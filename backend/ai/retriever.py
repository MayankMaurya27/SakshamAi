"""RAG retrieval service for document and Saksham knowledge base."""

import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from ai.embeddings import embed_text
from ai.faiss_manager import get_saksham_index, get_user_index
from config.settings import get_settings
from database.repositories import ChunkRepository
from services.curriculum_utils import chapter_matches

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ChunkContext:
    """Retrieved chunk with metadata."""

    text: str
    score: float
    faiss_id: int
    metadata: dict


def retrieve_document_context(
    question: str,
    db: Session,
    document_id: int | None = None,
    top_k: int | None = None,
) -> list[ChunkContext]:
    """Retrieve relevant chunks from user document index."""
    query_vector = embed_text(question, is_query=True)
    user_index = get_user_index()
    results = user_index.search(query_vector, top_k=top_k)

    if not results:
        logger.info("No results from user index for query")
        return []

    faiss_ids = [faiss_id for faiss_id, _, _ in results]
    chunk_repo = ChunkRepository(db)
    chunks = chunk_repo.get_by_faiss_ids(faiss_ids)
    chunk_by_faiss = {chunk.faiss_id: chunk for chunk in chunks}

    contexts: list[ChunkContext] = []
    for faiss_id, score, meta in results:
        chunk = chunk_by_faiss.get(faiss_id)
        if chunk is None:
            continue
        if document_id is not None and chunk.document_id != document_id:
            continue
        contexts.append(
            ChunkContext(
                text=chunk.chunk_text,
                score=score,
                faiss_id=faiss_id,
                metadata=meta,
            )
        )

    logger.info("Retrieved %d document chunks (document_id=%s)", len(contexts), document_id)
    return contexts


def _get_chapter_chunk_texts(
    class_level: int, subject: str, chapter_ref: str
) -> list[str]:
    """Return ordered chunk texts for a chapter from FAISS metadata."""
    saksham_index = get_saksham_index()
    chunks: list[tuple[int, str]] = []

    for faiss_id, meta in saksham_index.id_map.items():
        if not chapter_matches(meta, class_level, subject, chapter_ref):
            continue
        chunk_text = meta.get("chunk_text", "")
        chunk_index = meta.get("chunk_index", faiss_id)
        if chunk_text:
            chunks.append((chunk_index, chunk_text))

    chunks.sort(key=lambda x: x[0])
    return [text for _, text in chunks]


def retrieve_saksham_context(
    question: str,
    class_level: int,
    subject: str,
    chapter_ref: str,
    top_k: int | None = None,
) -> list[ChunkContext]:
    """
    Retrieve relevant chunks for a Saksham curriculum chapter.

    Uses chapter-scoped FAISS search first, then falls back to all chapter chunks
    in document order if semantic search returns nothing.
    """
    k = top_k or settings.top_k
    saksham_index = get_saksham_index()

    def chapter_filter(meta: dict) -> bool:
        return chapter_matches(meta, class_level, subject, chapter_ref)

    query_vector = embed_text(question, is_query=True)
    results = saksham_index.search_filtered(query_vector, chapter_filter, top_k=k)

    if results:
        contexts = [
            ChunkContext(
                text=meta.get("chunk_text", ""),
                score=score,
                faiss_id=faiss_id,
                metadata=meta,
            )
            for faiss_id, score, meta in results
            if meta.get("chunk_text")
        ]
        logger.info(
            "Retrieved %d saksham chunks via filtered search (class=%s, chapter=%s)",
            len(contexts),
            class_level,
            chapter_ref,
        )
        return contexts

    # Direct fallback: all chunks for this chapter in order
    chunk_texts = _get_chapter_chunk_texts(class_level, subject, chapter_ref)
    if chunk_texts:
        logger.info(
            "Using direct chapter fallback with %d chunks (class=%s, chapter=%s)",
            len(chunk_texts),
            class_level,
            chapter_ref,
        )
        return [
            ChunkContext(
                text=text,
                score=1.0,
                faiss_id=idx,
                metadata={"chunk_index": idx, "fallback": True},
            )
            for idx, text in enumerate(chunk_texts[:k])
        ]

    logger.info(
        "No saksham content for class=%s subject=%s chapter=%s",
        class_level,
        subject,
        chapter_ref,
    )
    return []
