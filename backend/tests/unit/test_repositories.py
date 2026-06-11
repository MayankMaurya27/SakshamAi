"""Unit tests for database repositories."""

from database.repositories import ChunkRepository, DocumentRepository, QuizRepository


def test_document_repository_crud(db_session):
    """Document repository should create and retrieve documents."""
    repo = DocumentRepository(db_session)
    doc = repo.create(
        filename="test.pdf",
        filepath="/uploads/test.pdf",
        summary="A test summary",
        key_concepts=[{"name": "Force", "description": "Push or pull"}],
    )

    assert doc.id is not None
    fetched = repo.get_by_id(doc.id)
    assert fetched is not None
    assert fetched.filename == "test.pdf"

    data = repo.to_dict(fetched)
    assert data["summary"] == "A test summary"
    assert len(data["key_concepts"]) == 1


def test_chunk_repository(db_session):
    """Chunk repository should store and retrieve chunks."""
    doc_repo = DocumentRepository(db_session)
    doc = doc_repo.create(filename="test.pdf", filepath="/uploads/test.pdf")

    chunk_repo = ChunkRepository(db_session)
    chunks = chunk_repo.create_batch(
        doc.id,
        [(0, "First chunk text", 0), (1, "Second chunk text", 1)],
    )
    assert len(chunks) == 2

    by_faiss = chunk_repo.get_by_faiss_ids([0, 1])
    assert len(by_faiss) == 2


def test_quiz_repository(db_session):
    """Quiz repository should store and retrieve quizzes."""
    doc_repo = DocumentRepository(db_session)
    doc = doc_repo.create(filename="test.pdf", filepath="/uploads/test.pdf")

    quiz_repo = QuizRepository(db_session)
    quiz_repo.create_batch(
        doc.id,
        [
            {
                "question": "What is force?",
                "option_a": "Push or pull",
                "option_b": "Color",
                "option_c": "Sound",
                "option_d": "Light",
                "correct_answer": "A",
            }
        ],
    )

    quizzes = quiz_repo.get_by_document_id(doc.id)
    assert len(quizzes) == 1
    data = quiz_repo.to_dict_list(quizzes)
    assert data[0]["question"] == "What is force?"
