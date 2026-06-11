"""Shared test fixtures and mocks."""

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ai.embeddings import MockEmbeddings, set_embedding_model
from ai.faiss_manager import FaissManager, reset_indexes_for_testing
from ai.llm import MockLLM, set_llm
from config.settings import Settings, get_settings
from database.db import get_db
from database.models import Base


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Create settings pointing to a temporary data directory."""
    tmp_dir = tempfile.mkdtemp(prefix="saksham_test_")
    settings = Settings(
        data_dir=Path(tmp_dir),
        uploads_dir=Path(tmp_dir) / "uploads",
        faiss_dir=Path(tmp_dir) / "faiss",
        audio_dir=Path(tmp_dir) / "audio",
        saksham_kb_dir=Path(tmp_dir) / "saksham_kb",
        database_url=f"sqlite:///{tmp_dir}/test.db",
    )
    settings.ensure_directories()
    return settings


@pytest.fixture(autouse=True)
def setup_mocks(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Configure mock AI services for all tests."""
    reset_indexes_for_testing()
    set_embedding_model(MockEmbeddings(dimension=384))
    set_llm(MockLLM())

    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    get_settings.cache_clear()
    yield
    reset_indexes_for_testing()
    get_settings.cache_clear()


@pytest.fixture
def db_session(test_settings: Settings) -> Generator[Session, None, None]:
    """Provide an in-memory database session."""
    engine = create_engine(
        test_settings.database_url,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def faiss_manager() -> FaissManager:
    """Provide a fresh FAISS manager for unit tests."""
    manager = FaissManager(name="test_index", dimension=384)
    manager.create_index()
    return manager


@pytest.fixture
def client(test_settings: Settings, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Provide FastAPI test client with overridden dependencies."""
    monkeypatch.setattr("config.settings.get_settings", lambda: test_settings)
    monkeypatch.setattr("database.db.settings", test_settings)

    engine = create_engine(
        test_settings.database_url,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        session = TestSession()
        try:
            yield session
        finally:
            session.close()

    from app import app

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
