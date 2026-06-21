"""File-based summary cache for Saksham chapters."""

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
    path = settings.summary_cache_dir
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_key(
    source: str,
    class_level: int | None = None,
    subject: str | None = None,
    chapter_id: str | None = None,
    document_id: int | None = None,
    accessibility_profile: str | None = None,
) -> str:
    parts = [
        source,
        settings.summary_cache_version,
        str(class_level or ""),
        (subject or "").lower(),
        (chapter_id or "").lower(),
        str(document_id or ""),
        (accessibility_profile or "").lower(),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]


def cache_path(
    source: str,
    class_level: int | None = None,
    subject: str | None = None,
    chapter_id: str | None = None,
    document_id: int | None = None,
    accessibility_profile: str | None = None,
) -> Path:
    key = _cache_key(
        source,
        class_level=class_level,
        subject=subject,
        chapter_id=chapter_id,
        document_id=document_id,
        accessibility_profile=accessibility_profile,
    )
    return _cache_dir() / f"{key}.json"


def load_cached_summary(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and payload.get("summary"):
            logger.info("Summary cache hit: %s", path.name)
            return payload
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Ignoring invalid summary cache %s: %s", path, exc)
    return None


def save_cached_summary(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Saved summary cache: %s", path.name)
