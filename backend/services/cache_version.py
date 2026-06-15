"""Purge file caches when their configured version changes."""

from __future__ import annotations

import logging
from pathlib import Path

from config.settings import Settings

logger = logging.getLogger(__name__)

_VERSION_MARKER = ".cache_version"


def _read_marker(marker_path: Path) -> str | None:
    if not marker_path.is_file():
        return None
    try:
        value = marker_path.read_text(encoding="utf-8").strip()
        return value or None
    except OSError as exc:
        logger.warning("Could not read cache version marker %s: %s", marker_path, exc)
        return None


def _write_marker(marker_path: Path, version: str) -> None:
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.write_text(version, encoding="utf-8")


def purge_cache_dir_if_version_changed(
    cache_dir: Path,
    current_version: str,
    label: str,
) -> int:
    """
    Delete stale JSON cache files when `current_version` differs from the marker.

    Returns the number of removed cache files.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    marker_path = cache_dir / _VERSION_MARKER
    stored_version = _read_marker(marker_path)

    if stored_version is None:
        _write_marker(marker_path, current_version)
        logger.info("Initialized %s cache version marker: %s", label, current_version)
        return 0

    if stored_version == current_version:
        return 0

    removed = 0
    for cache_file in cache_dir.glob("*.json"):
        try:
            cache_file.unlink()
            removed += 1
        except OSError as exc:
            logger.warning("Could not remove stale %s cache %s: %s", label, cache_file, exc)

    _write_marker(marker_path, current_version)
    logger.info(
        "Purged %d stale %s cache file(s): %s -> %s",
        removed,
        label,
        stored_version,
        current_version,
    )
    return removed


def purge_caches_on_version_change(settings: Settings) -> dict[str, int]:
    """Purge summary and quiz file caches when their version settings change."""
    summary_version = settings.summary_cache_version
    quiz_version = f"{settings.quiz_cache_version}|{settings.saksham_index_version}"

    return {
        "summary_removed": purge_cache_dir_if_version_changed(
            settings.summary_cache_dir,
            summary_version,
            "summary",
        ),
        "quiz_removed": purge_cache_dir_if_version_changed(
            settings.quiz_cache_dir,
            quiz_version,
            "quiz",
        ),
        "localize_removed": purge_cache_dir_if_version_changed(
            settings.localize_cache_dir,
            settings.localize_cache_version,
            "localize",
        ),
    }
