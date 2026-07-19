"""File-based quiz explanation cache."""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _cache_dir() -> Path:
    path = settings.base_dir / "data" / "explain_cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_key(question: str) -> str:
    """Generate a hash for a question text."""
    digest = hashlib.sha256(question.strip().lower().encode("utf-8")).hexdigest()[:24]
    return digest


def cache_path(question: str) -> Path:
    """Return the JSON cache file path for an explanation request."""
    key = _cache_key(question)
    return _cache_dir() / f"{key}.json"


def load_cached_explanation(question: str) -> dict[str, Any] | None:
    """Load cached explanation payload if present."""
    path = cache_path(question)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and payload.get("why_correct"):
            logger.info("Explanation cache hit: %s", path.name)
            return payload
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Ignoring invalid explanation cache %s: %s", path, exc)
    return None


def save_cached_explanation(question: str, payload: dict[str, Any]) -> None:
    """Persist explanation payload to disk."""
    path = cache_path(question)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Saved explanation cache: %s", path.name)
