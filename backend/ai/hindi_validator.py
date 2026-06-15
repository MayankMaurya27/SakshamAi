"""Validation helpers for Hinenglish localization output."""

from __future__ import annotations

import json
import re
from typing import Any

from ai.hindi_formatter import devanagari_ratio

MIN_DEVANAGARI_RATIO = 0.35
QUIZ_FIELDS = ("question", "option_a", "option_b", "option_c", "option_d", "correct_answer")
VALID_ANSWERS = {"A", "B", "C", "D"}


def validate_prose_hindi(text: str) -> tuple[bool, str]:
    """Return (ok, reason) for Hinenglish prose output."""
    cleaned = text.strip()
    if not cleaned:
        return False, "Empty Hindi output."
    ratio = devanagari_ratio(cleaned)
    if ratio < MIN_DEVANAGARI_RATIO:
        return False, f"Insufficient Devanagari content (ratio={ratio:.2f})."
    return True, ""


def parse_quiz_question_json(raw: str) -> dict[str, str] | None:
    """Parse LLM JSON for one translated quiz question."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    result: dict[str, str] = {}
    for field in QUIZ_FIELDS:
        value = payload.get(field)
        if value is None:
            return None
        result[field] = str(value).strip()
    return result


def validate_quiz_question(
    translated: dict[str, str],
    original: dict[str, str],
) -> tuple[bool, str]:
    """Ensure translated quiz question preserves structure."""
    answer = translated.get("correct_answer", "").strip().upper()
    if answer not in VALID_ANSWERS:
        return False, f"Invalid correct_answer: {answer}"
    expected = str(original.get("correct_answer", "")).strip().upper()
    if expected and answer != expected:
        return False, f"correct_answer changed from {expected} to {answer}"
    for field in ("question", "option_a", "option_b", "option_c", "option_d"):
        if not translated.get(field, "").strip():
            return False, f"Missing translated field: {field}"
        ratio = devanagari_ratio(translated[field])
        if ratio < MIN_DEVANAGARI_RATIO:
            return False, f"Field {field} has insufficient Devanagari (ratio={ratio:.2f})."
    return True, ""


def validate_quiz_payload(
    translated_questions: list[dict[str, str]],
    original_questions: list[dict[str, Any]],
) -> tuple[bool, str]:
    if len(translated_questions) != len(original_questions):
        return False, "Question count mismatch."
    for idx, (translated, original) in enumerate(
        zip(translated_questions, original_questions, strict=True)
    ):
        ok, reason = validate_quiz_question(translated, original)
        if not ok:
            return False, f"Question {idx + 1}: {reason}"
    return True, ""
