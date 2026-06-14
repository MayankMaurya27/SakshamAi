"""File-based quiz cache for stateless clients (no login/signup)."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _cache_dir() -> Path:
    path = settings.quiz_cache_dir
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_key(
    source: str,
    question_count: int,
    class_level: int | None = None,
    subject: str | None = None,
    chapter_id: str | None = None,
    document_id: int | None = None,
) -> str:
    parts = [
        source,
        settings.saksham_index_version,
        settings.quiz_cache_version,
        str(question_count),
    ]
    if source == "saksham":
        parts.extend(
            [
                str(class_level or ""),
                (subject or "").lower(),
                (chapter_id or "").lower(),
            ]
        )
    else:
        parts.append(str(document_id or ""))
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return digest


def cache_path(
    source: str,
    question_count: int,
    class_level: int | None = None,
    subject: str | None = None,
    chapter_id: str | None = None,
    document_id: int | None = None,
) -> Path:
    """Return the JSON cache file path for a quiz request."""
    key = _cache_key(
        source,
        question_count,
        class_level=class_level,
        subject=subject,
        chapter_id=chapter_id,
        document_id=document_id,
    )
    return _cache_dir() / f"{key}.json"


def load_cached_quiz(path: Path) -> dict[str, Any] | None:
    """Load cached quiz payload if present."""
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and payload.get("questions"):
            logger.info("Quiz cache hit: %s", path.name)
            return payload
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Ignoring invalid quiz cache %s: %s", path, exc)
    return None


def save_cached_quiz(path: Path, payload: dict[str, Any]) -> None:
    """Persist quiz payload to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Saved quiz cache: %s", path.name)
