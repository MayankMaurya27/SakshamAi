"""File-based cache for Hinenglish localization."""

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
    path = settings.localize_cache_dir
    path.mkdir(parents=True, exist_ok=True)
    return path


def cache_key(
    english_source: str,
    content_type: str,
    class_level: int | None = None,
) -> str:
    parts = [
        settings.localize_cache_version,
        content_type,
        str(class_level or ""),
        english_source,
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]


def cache_path(
    english_source: str,
    content_type: str,
    class_level: int | None = None,
) -> Path:
    key = cache_key(english_source, content_type, class_level=class_level)
    return _cache_dir() / f"{key}.json"


def load_cached_localize(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and payload.get("language") == "hi":
            logger.info("Localize cache hit: %s", path.name)
            payload["cached"] = True
            return payload
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Ignoring invalid localize cache %s: %s", path, exc)
    return None


def save_cached_localize(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    to_save = dict(payload)
    to_save["cached"] = False
    path.write_text(json.dumps(to_save, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Saved localize cache: %s", path.name)
