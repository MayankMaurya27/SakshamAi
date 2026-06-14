"""Document lifecycle helpers: delete uploads and rebuild search index."""

from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy.orm import Session

from ai.faiss_manager import get_user_index, reset_user_index, save_user_index
from ai.embeddings import embed_batch
from database.repositories import ChunkRepository, DocumentRepository
from exceptions import DocumentNotFoundError

logger = logging.getLogger(__name__)


def _remove_upload_file(filepath: str) -> None:
    path = Path(filepath)
    if path.is_file():
        path.unlink()
        logger.info("Removed upload file: %s", path)


def rebuild_user_index(db: Session) -> None:
    """Rebuild the user FAISS index from all document chunks still in the database."""
    reset_user_index()
    user_index = get_user_index()
    chunk_repo = ChunkRepository(db)
    doc_repo = DocumentRepository(db)

    for document in doc_repo.list_all():
        chunks = chunk_repo.get_by_document_id(document.id)
        if not chunks:
            continue

        texts = [chunk.chunk_text for chunk in chunks]
        vectors = embed_batch(texts, is_query=False)
        metadata_list = [
            {
                "source": "user_document",
                "document_id": document.id,
                "chunk_text": chunk.chunk_text,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ]
        faiss_ids = user_index.add_vectors(vectors, metadata_list)
        for chunk, faiss_id in zip(chunks, faiss_ids):
            chunk.faiss_id = faiss_id

    db.commit()
    save_user_index()
    logger.info("Rebuilt user FAISS index with %d vectors", user_index.total_vectors)


def delete_document(document_id: int, db: Session) -> None:
    """Delete a document, its PDF on disk, and rebuild the user FAISS index."""
    doc_repo = DocumentRepository(db)
    document = doc_repo.get_by_id(document_id)
    if document is None:
        raise DocumentNotFoundError(f"Document {document_id} not found.")

    _remove_upload_file(document.filepath)
    doc_repo.delete_by_id(document_id)
    rebuild_user_index(db)
    logger.info("Deleted document_id=%d", document_id)


def purge_all_uploads(db: Session, uploads_dir: Path) -> dict[str, int]:
    """Remove every PDF in uploads/, clear document records, and reset the user index."""
    removed_files = 0
    for pdf_path in uploads_dir.glob("*.pdf"):
        pdf_path.unlink(missing_ok=True)
        removed_files += 1

    doc_repo = DocumentRepository(db)
    deleted_documents = doc_repo.delete_all()
    reset_user_index()
    save_user_index()

    logger.info(
        "Purged uploads: removed_files=%d deleted_documents=%d",
        removed_files,
        deleted_documents,
    )
    return {
        "removed_files": removed_files,
        "deleted_documents": deleted_documents,
    }
