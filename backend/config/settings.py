"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for Saksham AI backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "Saksham AI Backend"
    debug: bool = False

    # Paths (relative to backend/ directory)
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    uploads_dir: Path = data_dir / "uploads"
    faiss_dir: Path = data_dir / "faiss"
    audio_dir: Path = data_dir / "audio"
    saksham_kb_dir: Path = data_dir / "saksham_kb"
    models_dir: Path = data_dir / "models"
    database_url: str = "sqlite:///./data/saksham.db"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:1b"
    ollama_timeout_seconds: float = 120.0
    ollama_temperature: float = 0.1
    ollama_num_ctx: int = 8192

    # Embeddings
    embedding_model: str = "intfloat/multilingual-e5-small"
    # Optional absolute path to a bundled model dir (Jetson); overrides HF cache lookup
    embedding_model_path: Path | None = None
    # Use local cache only (required for offline/Jetson — avoids HuggingFace network retries)
    embedding_local_files_only: bool = True
    preload_embedding_model: bool = True

    # FAISS index files
    user_index_path: Path = faiss_dir / "user_index.faiss"
    user_index_meta_path: Path = faiss_dir / "user_index_meta.json"
    saksham_index_path: Path = faiss_dir / "saksham_index.faiss"
    saksham_index_meta_path: Path = faiss_dir / "saksham_index_meta.json"
    saksham_kb_hash_path: Path = faiss_dir / "saksham_kb_hash.txt"
    saksham_bm25_index_path: Path = faiss_dir / "saksham_bm25_index.json"

    # Piper TTS
    piper_binary: str = "piper"
    piper_model_path: str = ""

    # Retrieval / hybrid search
    top_k: int = 5
    top_k_guided: int = 7
    max_llm_context_chars: int = 3200
    max_llm_context_chars_guided: int = 7000
    chunk_size_tokens: int = 700
    chunk_overlap_tokens: int = 100
    retrieval_candidate_count: int = 20
    rrf_k: int = 60
    bm25_enabled: bool = True
    hybrid_retrieval_enabled: bool = True
    rerank_enabled: bool = True
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    rerank_model_path: Path | None = None
    rerank_local_files_only: bool = True
    rerank_top_k: int = 7
    saksham_index_version: str = "v2-section-hybrid"

    # Quiz generation
    quiz_cache_dir: Path = data_dir / "quiz_cache"
    quiz_min_questions: int = 5
    quiz_max_questions: int = 15
    quiz_default_questions: int = 10
    quiz_max_context_chars: int = 6500
    ollama_num_predict_quiz: int = 2048
    quiz_llm_max_attempts: int = 5
    quiz_llm_batch_size: int = 1
    quiz_cache_version: str = "v11-quality-gate"

    # Summary generation
    summary_cache_dir: Path = data_dir / "summary_cache"
    summary_cache_version: str = "v2-prose-grounded"
    summary_max_context_chars: int = 6500
    summary_max_chars: int = 5000
    summary_min_words: int = 260
    summary_target_words: int = 380
    summary_min_paragraphs: int = 4
    summary_map_reduce_windows: int = 3
    ollama_num_predict_summary: int = 3200

    # Dyslexia-friendly formatting
    dyslexia_max_words_per_sentence: int = 15
    dyslexia_max_bullets: int = 8

    def ensure_directories(self) -> None:
        """Create required data directories if they do not exist."""
        for directory in (
            self.data_dir,
            self.uploads_dir,
            self.faiss_dir,
            self.audio_dir,
            self.saksham_kb_dir,
            self.models_dir,
            self.quiz_cache_dir,
            self.summary_cache_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

        for class_level in range(6, 11):
            (self.saksham_kb_dir / f"class{class_level}").mkdir(parents=True, exist_ok=True)

    @property
    def resolved_database_url(self) -> str:
        """Return database URL with absolute path for SQLite."""
        if self.database_url.startswith("sqlite:///"):
            if self.database_url.startswith("sqlite:///./"):
                relative = self.database_url.replace("sqlite:///./", "")
                db_path = self.base_dir / relative
            else:
                db_path = Path(self.database_url.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{db_path}"
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    settings = Settings()
    settings.ensure_directories()
    return settings
