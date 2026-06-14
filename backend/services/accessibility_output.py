"""Build accessibility-enriched API payloads."""

from __future__ import annotations

import logging
from typing import Any, Iterable

from ai.dyslexia_formatter import format_dyslexia_text, split_reading_segments
from config.constants import AccessibilityProfile
from config.settings import get_settings
from exceptions import ServiceUnavailableError
from services.audio_service import generate_audio

logger = logging.getLogger(__name__)
settings = get_settings()

DYSLEXIA_DISPLAY_HINTS: dict[str, Any] = {
    "line_height": 1.5,
    "max_line_chars": 60,
    "font_family": "sans-serif",
    "letter_spacing": "0.03em",
    "word_spacing": "0.05em",
    "background": "#FFF8E7",
    "prefer_audio": True,
}


def display_hints_for(profile: AccessibilityProfile) -> dict[str, Any]:
    if profile == AccessibilityProfile.DYSLEXIA:
        return dict(DYSLEXIA_DISPLAY_HINTS)
    return {}


def format_text_for_profile(
    text: str,
    profile: AccessibilityProfile,
    preserve_terms: Iterable[str] | None = None,
) -> str:
    if profile == AccessibilityProfile.DYSLEXIA:
        return format_dyslexia_text(text, preserve_terms=preserve_terms)
    return text


def _maybe_generate_audio(
    text: str,
    include_audio: bool,
    *,
    segments: list[str] | None = None,
) -> str | None:
    if not include_audio or not text.strip():
        return None
    try:
        result = generate_audio(text, segments=segments)
        return result.get("audio_path")
    except ServiceUnavailableError as exc:
        logger.warning("Audio generation skipped: %s", exc.message)
        return None


def build_accessibility_metadata(
    profile: AccessibilityProfile,
    formatted_text: str,
    *,
    include_audio: bool = False,
) -> dict[str, Any]:
    """Build accessibility metadata for already-formatted text."""
    segments = split_reading_segments(formatted_text) if profile == AccessibilityProfile.DYSLEXIA else []
    audio_path = _maybe_generate_audio(
        formatted_text,
        include_audio,
        segments=segments if segments else None,
    )
    return {
        "profile": profile.value,
        "display_hints": display_hints_for(profile),
        "reading_segments": segments,
        "audio_path": audio_path,
    }


def build_accessibility_payload(
    profile: AccessibilityProfile,
    text: str,
    *,
    include_audio: bool = False,
    preserve_terms: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Format text and return accessibility metadata for API responses."""
    formatted = format_text_for_profile(text, profile, preserve_terms=preserve_terms)
    metadata = build_accessibility_metadata(profile, formatted, include_audio=include_audio)
    return {
        "profile": metadata["profile"],
        "formatted_text": formatted,
        "display_hints": metadata["display_hints"],
        "reading_segments": metadata["reading_segments"],
        "audio_path": metadata["audio_path"],
    }


def enrich_response_data(
    data: dict[str, Any],
    text_key: str,
    profile: AccessibilityProfile | None,
    *,
    include_audio: bool = False,
    preserve_terms: Iterable[str] | None = None,
    already_formatted: bool = False,
) -> dict[str, Any]:
    """Attach formatted text and accessibility block to an existing response dict."""
    if profile is None:
        return data

    source_text = str(data.get(text_key, "") or "")
    if already_formatted:
        formatted = source_text
    else:
        formatted = format_text_for_profile(source_text, profile, preserve_terms=preserve_terms)
        data[text_key] = formatted

    metadata = build_accessibility_metadata(profile, formatted, include_audio=include_audio)
    data["accessibility"] = metadata
    return data
