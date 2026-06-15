"""Tests for pre-built index loading without source PDFs."""

from ai.faiss_manager import reset_indexes_for_testing
from config.settings import Settings
from services.knowledge_service import _prebuilt_index_available, build_saksham_index, list_chapters


def test_prebuilt_index_available():
    """Pre-built index files should exist after curriculum ingest."""
    settings = Settings()
    assert settings.saksham_index_path.exists()
    assert settings.saksham_index_meta_path.exists()
    assert _prebuilt_index_available()


def test_startup_without_pdfs():
    """Server startup should load index even when curriculum PDFs are removed."""
    reset_indexes_for_testing()
    build_saksham_index(force=False)

    chapters = list_chapters(8, "Science")
    assert len(chapters) >= 13

    reset_indexes_for_testing()
