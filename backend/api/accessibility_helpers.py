"""Helper to enrich API responses with accessibility metadata."""

from __future__ import annotations

from typing import Any

from config.constants import AccessibilityProfile
from services.accessibility_output import enrich_response_data


def with_accessibility(
    data: dict[str, Any],
    text_key: str,
    profile: AccessibilityProfile | None,
    *,
    include_audio: bool = False,
    already_formatted: bool = False,
) -> dict[str, Any]:
    return enrich_response_data(
        data,
        text_key,
        profile,
        include_audio=include_audio,
        already_formatted=already_formatted,
    )
