"""English-to-Hinenglish localization service (translate-only, no RAG)."""

from __future__ import annotations

import json
import logging
from typing import Any

from ai.hindi_formatter import (
    extract_preserve_terms_from_english,
    split_reading_segments,
)
from ai.hindi_localize_prompt import (
    build_prose_localize_prompt,
    build_quiz_question_localize_prompt,
)
from ai.hindi_validator import (
    parse_quiz_question_json,
    validate_prose_hindi,
    validate_quiz_payload,
    validate_quiz_question,
)
from ai.llm import get_llm
from config.constants import LocalizeContentType
from config.settings import get_settings
from exceptions import ServiceUnavailableError, ValidationError
from services.audio_service import generate_audio
from services.localize_cache import cache_path, load_cached_localize, save_cached_localize

logger = logging.getLogger(__name__)
settings = get_settings()

QUIZ_OPTION_KEYS = ("option_a", "option_b", "option_c", "option_d")


def _merge_preserve_terms(
    english_text: str,
    preserve_terms: list[str] | None,
) -> list[str]:
    merged = list(preserve_terms or [])
    merged.extend(extract_preserve_terms_from_english(english_text))
    return list(dict.fromkeys(term.strip() for term in merged if term.strip()))


def _cache_source_for_quiz(questions: list[dict[str, Any]]) -> str:
    return json.dumps(questions, ensure_ascii=False, sort_keys=True)


def _translate_prose(
    english_text: str,
    content_type: LocalizeContentType,
    *,
    class_level: int | None,
    preserve_terms: list[str] | None,
) -> str:
    llm = get_llm()
    terms = _merge_preserve_terms(english_text, preserve_terms)

    for strict_retry in (False, True):
        prompt = build_prose_localize_prompt(
            english_text,
            content_type,
            class_level=class_level,
            preserve_terms=terms,
            strict_retry=strict_retry,
        )
        hindi_text = llm.generate(
            prompt,
            num_predict=settings.ollama_num_predict_localize,
        ).strip()
        ok, reason = validate_prose_hindi(hindi_text)
        if ok:
            return hindi_text
        logger.warning(
            "Hinenglish validation failed (retry=%s): %s",
            strict_retry,
            reason,
        )

    raise ValidationError(
        "Could not produce valid Hinenglish output. Try again or shorten the English text."
    )


def _translate_quiz_question(
    question: dict[str, str],
    *,
    class_level: int | None,
) -> dict[str, str]:
    llm = get_llm()
    original = {key: str(question.get(key, "")) for key in (
        "question", *QUIZ_OPTION_KEYS, "correct_answer"
    )}

    for strict_retry in (False, True):
        prompt = build_quiz_question_localize_prompt(
            original,
            class_level=class_level,
            strict_retry=strict_retry,
        )
        raw = llm.generate(
            prompt,
            num_predict=settings.ollama_num_predict_localize,
            format_json=True,
        )
        translated = parse_quiz_question_json(raw)
        if translated is None:
            logger.warning("Quiz JSON parse failed (retry=%s)", strict_retry)
            continue
        ok, reason = validate_quiz_question(translated, original)
        if ok:
            return translated
        logger.warning("Quiz validation failed (retry=%s): %s", strict_retry, reason)

    raise ValidationError("Could not translate quiz question to valid Hinenglish.")


def _translate_quiz(
    questions: list[dict[str, Any]],
    *,
    class_level: int | None,
) -> list[dict[str, str]]:
    translated: list[dict[str, str]] = []
    for question in questions:
        normalized = {
            "question": str(question.get("question", "")),
            "option_a": str(question.get("option_a", "")),
            "option_b": str(question.get("option_b", "")),
            "option_c": str(question.get("option_c", "")),
            "option_d": str(question.get("option_d", "")),
            "correct_answer": str(question.get("correct_answer", "A")).strip().upper(),
        }
        translated.append(_translate_quiz_question(normalized, class_level=class_level))

    ok, reason = validate_quiz_payload(translated, questions)
    if not ok:
        raise ValidationError(f"Quiz localization failed: {reason}")
    return translated


def _maybe_attach_audio(
    hindi_text: str,
    include_audio: bool,
    segments: list[str] | None = None,
) -> str | None:
    if not include_audio or not hindi_text.strip():
        return None
    try:
        result = generate_audio(
            hindi_text,
            segments=segments,
            language="hi",
        )
        return result.get("audio_path")
    except (ServiceUnavailableError, ValidationError) as exc:
        logger.warning("Hindi audio generation skipped: %s", exc)
        return None


def localize_to_hindi(
    *,
    text: str | None,
    content_type: LocalizeContentType,
    quiz: dict[str, Any] | None = None,
    class_level: int | None = None,
    subject: str | None = None,
    include_audio: bool = False,
    preserve_terms: list[str] | None = None,
) -> dict[str, Any]:
    """
    Convert English content to Hinenglish.

    Does not run RAG — only translates provided English text or quiz payload.
    """
    _ = subject  # reserved for future subject-specific terminology

    if content_type == LocalizeContentType.QUIZ:
        if not quiz or not quiz.get("questions"):
            raise ValidationError("quiz.questions is required for quiz localization.")
        questions = quiz["questions"]
        cache_source = _cache_source_for_quiz(questions)
        path = cache_path(cache_source, content_type.value, class_level=class_level)
        cached = load_cached_localize(path)
        if cached:
            return cached

        hindi_questions = _translate_quiz(questions, class_level=class_level)
        hindi_quiz = {"questions": hindi_questions}
        quiz_text = "\n\n".join(
            f"• {item['question']}" for item in hindi_questions
        )
        segments = split_reading_segments(quiz_text)
        audio_path = _maybe_attach_audio(quiz_text, include_audio, segments=segments)

        payload: dict[str, Any] = {
            "language": "hi",
            "content_type": content_type.value,
            "hindi_quiz": hindi_quiz,
            "reading_segments": segments,
            "audio_path": audio_path,
            "cached": False,
        }
        save_cached_localize(path, payload)
        return payload

    if not text or not text.strip():
        raise ValidationError("text is required for prose localization.")

    path = cache_path(text, content_type.value, class_level=class_level)
    cached = load_cached_localize(path)
    if cached:
        return cached

    hindi_text = _translate_prose(
        text,
        content_type,
        class_level=class_level,
        preserve_terms=preserve_terms,
    )
    segments = split_reading_segments(hindi_text)
    audio_path = _maybe_attach_audio(hindi_text, include_audio, segments=segments)

    payload = {
        "language": "hi",
        "content_type": content_type.value,
        "hindi_text": hindi_text,
        "reading_segments": segments,
        "audio_path": audio_path,
        "cached": False,
    }
    save_cached_localize(path, payload)
    return payload
