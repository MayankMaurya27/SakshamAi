"""Unit tests for Saksham chapter-scoped retrieval."""

from ai.embeddings import MockEmbeddings, embed_text, set_embedding_model
from ai.faiss_manager import FaissManager, reset_indexes_for_testing
from ai import faiss_manager
from ai.retriever import retrieve_saksham_context


def test_retrieve_saksham_context_chapter_scoped():
    """Retrieval should return chunks scoped to the selected chapter."""
    reset_indexes_for_testing()
    set_embedding_model(MockEmbeddings(dimension=384))

    manager = FaissManager(name="saksham_index", dimension=384)
    manager.create_index()

    force_text = "Force is a push or pull that can change the motion of an object."
    other_text = "Fractions represent parts of a whole number in mathematics."

    vectors = embed_text(force_text)  # will use mock
    v2 = embed_text(other_text)
    import numpy as np

    batch = np.vstack([vectors, v2])
    manager.add_vectors(
        batch,
        [
            {
                "class": 8,
                "subject": "Science",
                "chapter_id": "exploring_forces",
                "chapter_title": "Exploring Forces",
                "chunk_text": force_text,
                "chunk_index": 0,
            },
            {
                "class": 7,
                "subject": "Mathematics",
                "chapter_id": "fractions",
                "chapter_title": "Fractions",
                "chunk_text": other_text,
                "chunk_index": 0,
            },
        ],
    )

    faiss_manager._saksham_index = manager

    contexts = retrieve_saksham_context(
        "What is force?",
        class_level=8,
        subject="Science",
        chapter_ref="Exploring Forces",
    )

    assert len(contexts) > 0
    assert all("force" in ctx.text.lower() for ctx in contexts)
    assert not any("fraction" in ctx.text.lower() for ctx in contexts)

    reset_indexes_for_testing()
