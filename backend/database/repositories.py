"""Repository pattern for database access."""

import json
from typing import Any

from sqlalchemy.orm import Session

from database.models import Chunk, Document, Quiz


class DocumentRepository:
    """Data access for documents."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        filename: str,
        filepath: str,
        summary: str | None = None,
        key_concepts: list[dict[str, str]] | None = None,
    ) -> Document:
        """Create a new document record."""
        document = Document(
            filename=filename,
            filepath=filepath,
            summary=summary,
            key_concepts=json.dumps(key_concepts) if key_concepts else None,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_by_id(self, document_id: int) -> Document | None:
        """Fetch a document by primary key."""
        return self.db.query(Document).filter(Document.id == document_id).first()

    def list_all(self) -> list[Document]:
        """Return all documents ordered by upload date descending."""
        return (
            self.db.query(Document)
            .order_by(Document.uploaded_at.desc())
            .all()
        )

    def update_analysis(
        self,
        document_id: int,
        summary: str,
        key_concepts: list[dict[str, str]],
    ) -> Document | None:
        """Update summary and key concepts after auto-analysis."""
        document = self.get_by_id(document_id)
        if document is None:
            return None
        document.summary = summary
        document.key_concepts = json.dumps(key_concepts)
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete_by_id(self, document_id: int) -> bool:
        """Delete a document record. Related chunks and quizzes cascade."""
        document = self.get_by_id(document_id)
        if document is None:
            return False
        self.db.delete(document)
        self.db.commit()
        return True

    def delete_all(self) -> int:
        """Delete all document records and related chunks/quizzes."""
        documents = self.list_all()
        for document in documents:
            self.db.delete(document)
        self.db.commit()
        return len(documents)

    def to_dict(self, document: Document) -> dict[str, Any]:
        """Serialize document to dictionary."""
        key_concepts: list[Any] = []
        if document.key_concepts:
            try:
                key_concepts = json.loads(document.key_concepts)
            except json.JSONDecodeError:
                key_concepts = []

        return {
            "id": document.id,
            "filename": document.filename,
            "filepath": document.filepath,
            "uploaded_at": document.uploaded_at.isoformat(),
            "summary": document.summary,
            "key_concepts": key_concepts,
        }


class ChunkRepository:
    """Data access for document chunks."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_batch(
        self,
        document_id: int,
        chunks: list[tuple[int, str, int]],
    ) -> list[Chunk]:
        """Create multiple chunks. Each tuple is (chunk_index, chunk_text, faiss_id)."""
        records = [
            Chunk(
                document_id=document_id,
                chunk_index=chunk_index,
                chunk_text=chunk_text,
                faiss_id=faiss_id,
            )
            for chunk_index, chunk_text, faiss_id in chunks
        ]
        self.db.add_all(records)
        self.db.commit()
        for record in records:
            self.db.refresh(record)
        return records

    def get_by_faiss_ids(self, faiss_ids: list[int]) -> list[Chunk]:
        """Fetch chunks by FAISS vector IDs."""
        if not faiss_ids:
            return []
        return (
            self.db.query(Chunk)
            .filter(Chunk.faiss_id.in_(faiss_ids))
            .all()
        )

    def get_by_document_id(self, document_id: int) -> list[Chunk]:
        """Fetch all chunks for a document."""
        return (
            self.db.query(Chunk)
            .filter(Chunk.document_id == document_id)
            .order_by(Chunk.chunk_index)
            .all()
        )


class QuizRepository:
    """Data access for quiz questions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_batch(self, document_id: int, questions: list[dict[str, str]]) -> list[Quiz]:
        """Store multiple quiz questions for a document."""
        records = [
            Quiz(
                document_id=document_id,
                question=q["question"],
                option_a=q["option_a"],
                option_b=q["option_b"],
                option_c=q["option_c"],
                option_d=q["option_d"],
                correct_answer=q["correct_answer"],
            )
            for q in questions
        ]
        self.db.add_all(records)
        self.db.commit()
        for record in records:
            self.db.refresh(record)
        return records

    def get_by_document_id(self, document_id: int) -> list[Quiz]:
        """Fetch all quiz questions for a document."""
        return (
            self.db.query(Quiz)
            .filter(Quiz.document_id == document_id)
            .all()
        )

    def delete_by_document_id(self, document_id: int) -> None:
        """Remove all quiz questions for a document."""
        self.db.query(Quiz).filter(Quiz.document_id == document_id).delete()
        self.db.commit()

    def to_dict_list(self, quizzes: list[Quiz]) -> list[dict[str, Any]]:
        """Serialize quiz records to dictionaries."""
        return [
            {
                "id": quiz.id,
                "question": quiz.question,
                "options": {
                    "A": quiz.option_a,
                    "B": quiz.option_b,
                    "C": quiz.option_c,
                    "D": quiz.option_d,
                },
                "correct_answer": quiz.correct_answer,
            }
            for quiz in quizzes
        ]
