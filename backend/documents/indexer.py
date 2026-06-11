"""Document indexing into FAISS."""

import logging
from typing import Any

from ai.embeddings import embed_batch
from ai.faiss_manager import FaissManager

logger = logging.getLogger(__name__)


def index_document(
    chunks: list[str],
    faiss_manager: FaissManager,
    metadata_base: dict[str, Any] | None = None,
) -> list[int]:
    """
    Generate embeddings and add document chunks to FAISS index.

    Args:
        chunks: Text chunks to index.
        faiss_manager: Target FAISS index manager.
        metadata_base: Base metadata to attach to each chunk.

    Returns:
        List of assigned FAISS IDs.
    """
    if not chunks:
        return []

    metadata_base = metadata_base or {}
    vectors = embed_batch(chunks, is_query=False)

    metadata_list = [
        {**metadata_base, "chunk_text": chunk, "chunk_index": idx}
        for idx, chunk in enumerate(chunks)
    ]

    faiss_ids = faiss_manager.add_vectors(vectors, metadata_list)
    logger.info("Indexed %d chunks into '%s'", len(faiss_ids), faiss_manager.name)
    return faiss_ids
