"""Document listing and detail endpoints."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.responses import error_response, success_response
from database.db import get_db
from database.repositories import DocumentRepository, QuizRepository

logger = logging.getLogger(__name__)
router = APIRouter(tags=["documents"])


@router.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    """Return list of uploaded documents."""
    doc_repo = DocumentRepository(db)
    documents = doc_repo.list_all()
    return success_response(
        {"documents": [doc_repo.to_dict(doc) for doc in documents]}
    )


@router.get("/document/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Return document details including stored quizzes."""
    doc_repo = DocumentRepository(db)
    document = doc_repo.get_by_id(document_id)
    if document is None:
        return error_response(f"Document {document_id} not found.", status_code=404)

    quiz_repo = QuizRepository(db)
    quizzes = quiz_repo.get_by_document_id(document_id)

    data = doc_repo.to_dict(document)
    data["quizzes"] = quiz_repo.to_dict_list(quizzes)
    return success_response(data)
