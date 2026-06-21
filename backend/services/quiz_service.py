"""Quiz generation for Saksham chapters and uploaded documents."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from sqlalchemy.orm import Session

from ai.dyslexia_formatter import extract_preserve_terms
from ai.llm import get_llm
from ai.prompt_builder import (
    build_quiz_prompt,
    build_concept_extraction_prompt,
    build_concept_quiz_prompt,
)
from config.constants import AccessibilityProfile, SourceType
from config.settings import get_settings
from database.repositories import ChunkRepository, DocumentRepository
from exceptions import DocumentNotFoundError, ValidationError
from services.accessibility_output import build_accessibility_metadata, format_text_for_profile
from services.knowledge_service import get_chapter_chunk_texts, validate_saksham_chapter
from services.quiz_cache import cache_path, load_cached_quiz, save_cached_quiz
from services.quiz_math import (
    build_chapter_quiz_questions,
    detect_math_chapter_kind,
    extract_valid_math_facts,
    filter_math_questions,
    format_math_facts_for_prompt,
    is_math_subject,
)
from services.quiz_science import (
    filter_science_questions,
    is_science_subject,
)
from services.quiz_context import filter_quiz_source_chunks, prepare_quiz_context
from services.quiz_grounded import (
    build_grounded_chapter_questions,
    filter_grounded_questions,
    strip_quiz_metadata,
    tag_llm_questions,
)

logger = logging.getLogger(__name__)
settings = get_settings()

_JSON_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.S)
_QUESTIONS_KEY = re.compile(r'"questions"\s*:\s*(\[)', re.I)
_QUESTION_OBJECT = re.compile(
    r'\{\s*"question"\s*:\s*"(?:\\.|[^"\\])*"(?:\s*,\s*"(?:option_[abcd]|correct_answer)"\s*:\s*"(?:\\.|[^"\\])*")*\s*\}',
    re.I | re.S,
)
_TEXT_QUESTION_BLOCK = re.compile(
    r"(?:^|\n)\s*(?:Question\s*)?(?P<num>\d+)\s*[.:)]\s*(?P<question>.+?)\s*\n"
    r"(?:A[.:)]\s*(?P<a>.+?)\s*\n)"
    r"(?:B[.:)]\s*(?P<b>.+?)\s*\n)"
    r"(?:C[.:)]\s*(?P<c>.+?)\s*\n)"
    r"(?:D[.:)]\s*(?P<d>.+?)\s*\n)"
    r"(?:Correct(?:\s+Answer)?|Answer)\s*[.:)]\s*(?P<answer>[ABCD])\b",
    re.I | re.S,
)
_TEXT_Q_BLOCK = re.compile(
    r"(?:^|\n)\s*Q(?:uestion)?\s*[.:)]\s*(?P<question>.+?)\s*\n"
    r"(?:A[.:)]\s*(?P<a>.+?)\s*\n)"
    r"(?:B[.:)]\s*(?P<b>.+?)\s*\n)"
    r"(?:C[.:)]\s*(?P<c>.+?)\s*\n)"
    r"(?:D[.:)]\s*(?P<d>.+?)\s*\n)"
    r"(?:Correct(?:\s+Answer)?|Answer)\s*[.:)]\s*(?P<answer>[ABCD])\b",
    re.I | re.S,
)


def _coerce_question_list(value: Any) -> list[dict]:
    """Normalize LLM question payloads into a list of dicts."""
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            parsed = _extract_bracketed_json(stripped, opening="[")
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
    return []


def _extract_bracketed_json(text: str, opening: str = "[") -> Any | None:
    """Extract a balanced JSON array or object substring."""
    closing = "]" if opening == "[" else "}"
    start = text.find(opening)
    if start < 0:
        return None

    depth = 0
    in_string = False
    escape = False
    for idx in range(start, len(text)):
        char = text[idx]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                snippet = text[start : idx + 1]
                try:
                    return json.loads(snippet)
                except json.JSONDecodeError:
                    if opening == "{" and snippet.rstrip().endswith("]"):
                        repaired = snippet.rstrip() + "}"
                        try:
                            return json.loads(repaired)
                        except json.JSONDecodeError:
                            return None
                    return None
    return None


def _parse_json_object_candidates(text: str) -> list[dict]:
    """Try parsing quiz JSON from several common LLM output shapes."""
    start = text.find("{")
    if start < 0:
        return []

    candidates: list[str] = []
    end = text.rfind("}") + 1
    if end > start:
        candidates.append(text[start:end])
    if text.rstrip().endswith("]"):
        candidates.append(text[start:].rstrip())
        if not text.rstrip().endswith("]}"):
            candidates.append(text[start:].rstrip() + "}")

    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            data = _extract_bracketed_json(candidate, opening="{")
            if data is None:
                continue
        if isinstance(data, list):
            return _coerce_question_list(data)
        if isinstance(data, dict):
            coerced = _coerce_question_list(data.get("questions"))
            if coerced:
                return coerced
    return []


def _extract_questions_array(text: str) -> list[dict]:
    """Extract the questions array even when the outer JSON object is truncated."""
    match = _QUESTIONS_KEY.search(text)
    if not match:
        return []
    array_start = match.start(1)
    parsed = _extract_bracketed_json(text[array_start:], opening="[")
    return _coerce_question_list(parsed)


def _extract_question_objects(text: str) -> list[dict]:
    """Last-resort extraction of individual question objects."""
    objects: list[dict] = []
    for match in _QUESTION_OBJECT.finditer(text):
        try:
            item = json.loads(match.group(0))
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict) and item.get("question"):
            objects.append(item)
    return objects


def _text_block_to_question(match: re.Match[str]) -> dict[str, str] | None:
    question = match.group("question").strip()
    options = {
        "A": match.group("a").strip(),
        "B": match.group("b").strip(),
        "C": match.group("c").strip(),
        "D": match.group("d").strip(),
    }
    answer = match.group("answer").strip().upper()
    if not question or not all(options.values()) or answer not in options:
        return None
    if len(set(options.values())) < 4:
        return None
    return {
        "question": question,
        "option_a": options["A"],
        "option_b": options["B"],
        "option_c": options["C"],
        "option_d": options["D"],
        "correct_answer": answer,
    }


def _parse_quiz_text_lines(text: str) -> list[dict]:
    """Parse MCQ blocks line-by-line, including inline Answer markers."""
    question_line = re.compile(
        r"^(?:Question\s*)?(?P<num>\d+)\s*[.:)]\s*(?P<question>.+)$",
        re.I,
    )
    q_line = re.compile(r"^Q(?:uestion)?\s*[.:)]\s*(?P<question>.+)$", re.I)
    option_line = re.compile(
        r"^([ABCD])[.:)]\s*(?P<text>.+?)(?:\(\s*(?:Correct(?:\s+Answer)?|Answer|Ans)\s*[.:)]\s*(?P<answer>[ABCD])\s*\))?\s*$",
        re.I,
    )
    answer_line = re.compile(
        r"^(?:Correct(?:\s+Answer)?|Answer|Ans)\s*[.:)]\s*(?P<answer>[ABCD])\b",
        re.I,
    )

    collected: list[dict] = []
    seen: set[str] = set()
    current: dict[str, str] = {}

    def flush() -> None:
        nonlocal current
        if not current.get("question"):
            current = {}
            return
        options = {
            letter: current.get(f"option_{letter.lower()}", "").strip()
            for letter in "ABCD"
        }
        answer = current.get("correct_answer", "").strip().upper()
        if not all(options.values()) or answer not in options:
            current = {}
            return
        if len(set(options.values())) < 4:
            current = {}
            return
        key = re.sub(r"\s+", " ", current["question"].lower()).strip()
        if key not in seen:
            seen.add(key)
            collected.append(
                {
                    "question": current["question"].strip(),
                    "option_a": options["A"],
                    "option_b": options["B"],
                    "option_c": options["C"],
                    "option_d": options["D"],
                    "correct_answer": answer,
                }
            )
        current = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            flush()
            continue

        match = question_line.match(line) or q_line.match(line)
        if match:
            flush()
            current = {"question": match.group("question").strip()}
            continue

        match = option_line.match(line)
        if match and current:
            letter = match.group(1).upper()
            current[f"option_{letter.lower()}"] = match.group("text").strip()
            if match.group("answer"):
                current["correct_answer"] = match.group("answer").upper()
            continue

        match = answer_line.match(line)
        if match and current:
            current["correct_answer"] = match.group("answer").upper()
            flush()
            continue

    flush()
    return collected


def parse_quiz_text_response(response: str) -> list[dict]:
    """Parse plain-text MCQ blocks from LLM output."""
    text = response.strip()
    if not text:
        return []

    collected: list[dict] = []
    seen: set[str] = set()
    for item in _parse_quiz_text_lines(text):
        key = re.sub(r"\s+", " ", item["question"].lower()).strip()
        if key in seen:
            continue
        seen.add(key)
        collected.append(item)

    for pattern in (_TEXT_QUESTION_BLOCK, _TEXT_Q_BLOCK):
        for match in pattern.finditer(text):
            item = _text_block_to_question(match)
            if item is None:
                continue
            key = re.sub(r"\s+", " ", item["question"].lower()).strip()
            if key in seen:
                continue
            seen.add(key)
            collected.append(item)
    return collected


def parse_quiz_response(response: str) -> list[dict]:
    """Parse quiz output from LLM response (plain text first, JSON fallback)."""
    text = response.strip()
    if not text:
        return []

    collected = parse_quiz_text_response(text)
    if collected:
        return collected

    fence = _JSON_FENCE.search(text)
    if fence:
        text = fence.group(1).strip()

    collected: list[dict] = []
    seen: set[str] = set()
    for extractor in (
        _parse_json_object_candidates,
        _extract_questions_array,
        _extract_question_objects,
    ):
        for item in extractor(text):
            if not isinstance(item, dict):
                continue
            question = str(item.get("question", "")).strip()
            if not question:
                continue
            key = re.sub(r"\s+", " ", question.lower()).strip()
            if key in seen:
                continue
            seen.add(key)
            collected.append(item)
    return collected


def clamp_question_count(question_count: int | None) -> int:
    """Clamp quiz size to configured bounds."""
    if question_count is None:
        return settings.quiz_default_questions
    return max(
        settings.quiz_min_questions,
        min(settings.quiz_max_questions, question_count),
    )


def normalize_questions(raw: list) -> list[dict[str, Any]]:
    """Normalize quiz questions to API format."""
    normalized: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        options = item.get("options")
        if not isinstance(options, dict):
            options = {
                "A": item.get("option_a", item.get("a", "")),
                "B": item.get("option_b", item.get("b", "")),
                "C": item.get("option_c", item.get("c", "")),
                "D": item.get("option_d", item.get("d", "")),
            }
        else:
            options = {
                "A": options.get("A", options.get("a", "")),
                "B": options.get("B", options.get("b", "")),
                "C": options.get("C", options.get("c", "")),
                "D": options.get("D", options.get("d", "")),
            }
        answer = str(item.get("correct_answer", "A")).strip().upper()
        if answer not in {"A", "B", "C", "D"}:
            answer = answer[:1] if answer[:1] in {"A", "B", "C", "D"} else "A"
        question = str(item.get("question", "")).strip()
        cleaned_options = {
            key: str(options.get(key, "")).strip()
            for key in ("A", "B", "C", "D")
        }
        if not question or not all(cleaned_options.values()):
            continue
        normalized.append(
            {
                "question": question,
                "options": cleaned_options,
                "correct_answer": answer,
            }
        )
    return normalized


def dedupe_questions(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove duplicate question text."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for question in questions:
        key = re.sub(r"\s+", " ", question["question"].lower()).strip()
        if key in seen:
            continue
        seen.add(key)
        unique.append(question)
    return unique


def validate_question_batch(
    questions: list[dict[str, Any]],
    minimum: int,
    maximum: int,
) -> list[dict[str, Any]]:
    """Validate and cap a quiz batch."""
    cleaned = dedupe_questions(questions)
    if len(cleaned) < minimum:
        raise ValidationError(
            f"Quiz generation produced only {len(cleaned)} valid questions; "
            f"minimum is {minimum}."
        )
    return cleaned[:maximum]


def _split_context_halves(context: str) -> tuple[str, str]:
    if "---" in context:
        parts = [part.strip() for part in context.split("---") if part.strip()]
        if len(parts) >= 2:
            mid = len(parts) // 2
            return "\n\n---\n\n".join(parts[:mid]), "\n\n---\n\n".join(parts[mid:])
    midpoint = len(context) // 2
    return context[:midpoint].strip(), context[midpoint:].strip()


def _filter_generated_batch(
    batch: list[dict[str, Any]],
    subject: str | None,
    corpus: str = "",
) -> list[dict[str, Any]]:
    if is_math_subject(subject):
        return filter_math_questions(batch)
    return filter_grounded_questions(batch, corpus)


def _context_for_attempt(context: str, attempt: int) -> str:
    """Rotate context on later attempts so retries are not identical."""
    if attempt <= 1 or len(context) <= 2500:
        return context
    offset = ((attempt - 1) * len(context)) // settings.quiz_llm_max_attempts
    rotated = context[offset:] + "\n\n---\n\n" + context[:offset]
    return rotated[: settings.quiz_max_context_chars]


def _generate_questions_for_context(
    context: str,
    question_count: int,
    topic: str,
    grade: int,
    subject: str | None = None,
    math_facts_reference: str = "",
    chapter_kind: str | None = None,
    exclude_questions: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    if not context.strip():
        raise ValidationError("No usable chapter content found for quiz generation.")

    llm = get_llm()
    collected: list[dict[str, Any]] = []
    max_attempts = settings.quiz_llm_max_attempts
    exclude_texts = [re.sub(r"\s+", " ", q["question"].lower()).strip() for q in (exclude_questions or [])]

    for attempt in range(1, max_attempts + 1):
        remaining = question_count - len(collected)
        if remaining <= 0:
            break

        batch_size = min(remaining, settings.quiz_llm_batch_size)
        attempt_context = _context_for_attempt(context, attempt)
        
        exclude_instruction = ""
        current_excludes = list(exclude_texts) + [re.sub(r"\s+", " ", q["question"].lower()).strip() for q in collected]
        if current_excludes:
            exclude_instruction = "\nDo NOT generate any of the following questions (avoid repeating these concepts):\n" + "\n".join(f"- {q}" for q in current_excludes)

        prompt = build_quiz_prompt(
            attempt_context,
            batch_size,
            topic=topic,
            grade=grade,
            subject=subject,
            math_facts_reference=math_facts_reference,
            chapter_kind=chapter_kind,
        )
        if exclude_instruction:
            prompt = prompt.rstrip() + "\n\n" + exclude_instruction

        response = llm.generate(
            prompt,
            num_predict=settings.ollama_num_predict_quiz,
            format_json=True,
        )
        batch = _filter_generated_batch(
            tag_llm_questions(
                normalize_questions(parse_quiz_response(response)),
                context,
            ),
            subject,
            context,
        )
        
        unique_batch = []
        for item in batch:
            key = re.sub(r"\s+", " ", item["question"].lower()).strip()
            if key not in exclude_texts:
                unique_batch.append(item)

        collected = dedupe_questions(collected + unique_batch)

        if len(collected) >= question_count:
            logger.info(
                "Quiz LLM succeeded on attempt %d/%d with %d questions for topic=%s",
                attempt,
                max_attempts,
                len(collected),
                topic,
            )
            return collected[:question_count]

        logger.warning(
            "Quiz LLM attempt %d/%d collected %d/%d valid questions for topic=%s",
            attempt,
            max_attempts,
            len(collected),
            question_count,
            topic,
        )

    return collected[:question_count]


def _generate_math_quiz_questions(
    context: str,
    question_count: int,
    topic: str,
    grade: int,
    subject: str,
    source_chunks: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Build math quizzes aligned to the chapter topic."""
    chunks = source_chunks or []
    standard_usable = filter_quiz_source_chunks(chunks)
    chapter_kind = detect_math_chapter_kind(standard_usable, topic)

    template_questions, _ = build_chapter_quiz_questions(
        standard_usable,
        question_count,
        chapter_title=topic,
    )
    remaining = max(0, question_count - len(template_questions))

    llm_questions: list[dict[str, Any]] = []
    if remaining > 0:
        facts = extract_valid_math_facts(standard_usable)
        llm_questions = _generate_questions_for_context(
            context,
            remaining,
            topic,
            grade,
            subject=subject,
            math_facts_reference=format_math_facts_for_prompt(facts),
            chapter_kind=chapter_kind,
        )

    combined = filter_math_questions(
        dedupe_questions(template_questions + llm_questions)
    )
    return combined[:question_count]


def _extract_concepts_from_context(context: str, topic: str, count: int) -> list[dict[str, str]]:
    """Extract key educational concepts from the text context using the local LLM."""
    if not context.strip():
        return []
    llm = get_llm()
    prompt = build_concept_extraction_prompt(context, topic=topic, concept_count=count)
    response = llm.generate(prompt, num_predict=settings.ollama_num_predict_quiz, format_json=True)
    
    text = response.strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "concepts" in data:
            return data["concepts"]
    except json.JSONDecodeError:
        pass
        
    fence = _JSON_FENCE.search(text)
    if fence:
        text = fence.group(1).strip()
        
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "concepts" in data:
            return data["concepts"]
    except json.JSONDecodeError:
        pass
        
    parsed = _extract_bracketed_json(text, opening="{")
    if isinstance(parsed, dict) and "concepts" in parsed:
        return parsed["concepts"]
        
    logger.warning("Failed to parse concept extraction JSON response. Using basic text fallback.")
    concepts = []
    names = re.findall(r'"concept_name"\s*:\s*"([^"]+)"', text)
    descriptions = re.findall(r'"concept_description"\s*:\s*"([^"]+)"', text)
    for name, desc in zip(names, descriptions):
        concepts.append({"concept_name": name, "concept_description": desc})
    return concepts


def _generate_questions_for_concepts(
    context: str,
    concepts: list[dict[str, str]],
    topic: str,
    grade: int,
    subject: str | None = None,
) -> list[dict[str, Any]]:
    """Query LLM to generate exactly 1 MCQ for each concept sequentially."""
    if not concepts:
        return []
        
    llm = get_llm()
    collected: list[dict[str, Any]] = []
    
    for idx, c in enumerate(concepts):
        concept_str = f"Concept: {c.get('concept_name')}\nDescription: {c.get('concept_description')}"
        
        exclude_instruction = ""
        if collected:
            exclude_texts = [re.sub(r"\s+", " ", q["question"].lower()).strip() for q in collected]
            exclude_instruction = "\nDo NOT generate any of the following questions (avoid repeating these concepts):\n" + "\n".join(f"- {q}" for q in exclude_texts)
            
        prompt = build_concept_quiz_prompt(
            retrieved_context=context,
            concepts_list=concept_str,
            question_count=1,
            topic=topic,
            grade=grade
        )
        if exclude_instruction:
            prompt = prompt.rstrip() + "\n\n" + exclude_instruction
            
        response = llm.generate(prompt, num_predict=settings.ollama_num_predict_quiz, format_json=True)
        parsed = parse_quiz_response(response)
        normalized = normalize_questions(parsed)
        tagged = tag_llm_questions(normalized, context)
        collected.extend(tagged)
        
    return collected


def _generate_grounded_quiz_questions(
    context: str,
    question_count: int,
    topic: str,
    grade: int,
    subject: str | None = None,
    source_chunks: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Build quizzes using concept-driven LLM flow first, then definitions/lists fallback."""
    chunks = source_chunks or []
    usable = filter_quiz_source_chunks(chunks, subject=subject)
    if not usable:
        usable = [chunk.strip() for chunk in chunks if chunk and chunk.strip()]
    corpus = "\n".join(usable)

    combined: list[dict[str, Any]] = []

    # 1. Primary Flow: Concept-Driven LLM Generation
    try:
        concepts_to_extract = max(10, question_count + 3)
        concepts = _extract_concepts_from_context(context, topic, concepts_to_extract)
        if concepts:
            llm_raw = _generate_questions_for_concepts(
                context,
                concepts,
                topic,
                grade,
                subject=subject
            )
            verified_llm = _filter_generated_batch(llm_raw, subject, corpus)
            combined = dedupe_questions(verified_llm)
            logger.info("Concept-driven flow generated %d verified questions", len(combined))
    except Exception as e:
        logger.error("Error in primary concept-driven flow: %s. Falling back.", e)

    # 2. Secondary Flow: Fallback to Heuristic-based Definitions & Lists (No Cloze)
    # Bypassed to eliminate mixed quiz styles (heuristics vs conceptual) and text recognition.
    remaining = max(0, question_count - len(combined))

    # 3. Final Fallback: If still short, try a standard LLM generation attempt for remaining count
    if remaining > 0:
        logger.info("Quiz still short by %d questions. Running final LLM fallback.", remaining)
        llm_raw = _generate_questions_for_context(
            context,
            remaining,
            topic,
            grade,
            subject=subject,
            exclude_questions=combined,
        )
        llm_questions = _filter_generated_batch(
            tag_llm_questions(normalize_questions(llm_raw), corpus),
            subject,
            corpus,
        )
        combined = dedupe_questions(combined + llm_questions)

    return strip_quiz_metadata(combined[:question_count])


def _generate_quiz_from_context(
    context: str,
    question_count: int,
    topic: str,
    grade: int,
    source_chunks: list[str] | None = None,
    subject: str | None = None,
) -> list[dict[str, Any]]:
    """Generate quiz questions, batching only for larger counts."""
    if is_math_subject(subject):
        questions = _generate_math_quiz_questions(
            context,
            question_count,
            topic,
            grade,
            subject or "",
            source_chunks,
        )
        return validate_question_batch(
            questions,
            settings.quiz_min_questions,
            question_count,
        )

    if is_science_subject(subject):
        questions = _generate_grounded_quiz_questions(
            context,
            question_count,
            topic,
            grade,
            subject=subject,
            source_chunks=source_chunks,
        )
        return validate_question_batch(
            questions,
            settings.quiz_min_questions,
            question_count,
        )

    use_batch = question_count > 7
    if not use_batch:
        questions = _generate_grounded_quiz_questions(
            context,
            question_count,
            topic,
            grade,
            subject=subject,
            source_chunks=source_chunks,
        )
        return validate_question_batch(
            questions,
            settings.quiz_min_questions,
            question_count,
        )

    first_count = question_count // 2
    second_count = question_count - first_count
    if source_chunks:
        usable = filter_quiz_source_chunks(source_chunks, subject=subject)
        if not usable:
            usable = [chunk for chunk in source_chunks if chunk and chunk.strip()]
        mid = max(1, len(usable) // 2)
        first_context = prepare_quiz_context(usable[:mid], subject=subject)
        second_context = prepare_quiz_context(usable[mid:], subject=subject)
    else:
        first_context, second_context = _split_context_halves(context)

    first_batch = _generate_grounded_quiz_questions(
        first_context,
        max(first_count, settings.quiz_min_questions),
        topic,
        grade,
        subject=subject,
        source_chunks=usable[:mid] if source_chunks else None,
    )
    second_batch = _generate_grounded_quiz_questions(
        second_context,
        max(second_count, settings.quiz_min_questions),
        topic,
        grade,
        subject=subject,
        source_chunks=usable[mid:] if source_chunks else None,
    )
    combined = dedupe_questions(first_batch + second_batch)
    return validate_question_batch(
        combined,
        settings.quiz_min_questions,
        question_count,
    )


def _build_response_payload(
    questions: list[dict[str, Any]],
    source: SourceType,
    question_count: int,
    class_level: int | None = None,
    subject: str | None = None,
    chapter: str | None = None,
    chapter_id: str | None = None,
    document_id: int | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "questions": questions,
        "question_count": len(questions),
        "requested_count": question_count,
        "source": source.value,
    }
    if source == SourceType.SAKSHAM:
        payload.update(
            {
                "class_level": class_level,
                "subject": subject,
                "chapter": chapter,
                "chapter_id": chapter_id,
            }
        )
    else:
        payload["document_id"] = document_id
    return payload


def generate_saksham_quiz(
    class_level: int,
    subject: str,
    chapter_ref: str,
    question_count: int | None = None,
) -> dict[str, Any]:
    """Generate a quiz for a Saksham curriculum chapter."""
    count = clamp_question_count(question_count)
    chapter = validate_saksham_chapter(class_level, subject, chapter_ref)
    chapter_id = chapter["chapter_id"]
    chapter_title = chapter.get("chapter_title") or chapter_ref

    cache_file = cache_path(
        SourceType.SAKSHAM.value,
        count,
        class_level=class_level,
        subject=subject,
        chapter_id=chapter_id,
    )
    cached = load_cached_quiz(cache_file)
    if cached:
        if (
            cached.get("chapter_id") == chapter_id
            and cached.get("class_level") == class_level
            and str(cached.get("subject", "")).lower() == subject.strip().lower()
        ):
            return cached
        logger.warning(
            "Ignoring quiz cache with mismatched metadata for chapter_id=%s",
            chapter_id,
        )

    chunks = get_chapter_chunk_texts(class_level, subject, chapter_ref)
    if not chunks:
        raise ValidationError(
            f"No indexed content for chapter '{chapter_ref}'. Run curriculum ingest."
        )

    context = prepare_quiz_context(chunks, subject=subject)
    questions = _generate_quiz_from_context(
        context,
        count,
        topic=chapter_title,
        grade=class_level,
        source_chunks=chunks,
        subject=subject,
    )
    payload = _build_response_payload(
        questions,
        SourceType.SAKSHAM,
        count,
        class_level=class_level,
        subject=subject,
        chapter=chapter_title,
        chapter_id=chapter_id,
    )
    save_cached_quiz(cache_file, payload)
    logger.info(
        "Generated Saksham quiz: class=%s subject=%s chapter=%s count=%d",
        class_level,
        subject,
        chapter_id,
        len(questions),
    )
    return payload


def generate_document_quiz(
    document_id: int,
    db: Session,
    question_count: int | None = None,
) -> dict[str, Any]:
    """Generate a quiz for an uploaded document."""
    count = clamp_question_count(question_count)
    doc_repo = DocumentRepository(db)
    document = doc_repo.get_by_id(document_id)
    if document is None:
        raise DocumentNotFoundError(f"Document {document_id} not found.")

    cache_file = cache_path(
        SourceType.DOCUMENT.value,
        count,
        document_id=document_id,
    )
    cached = load_cached_quiz(cache_file)
    if cached:
        if cached.get("document_id") == document_id:
            return cached
        logger.warning(
            "Ignoring quiz cache with mismatched document_id=%s",
            document_id,
        )

    chunks = ChunkRepository(db).get_by_document_id(document_id)
    if not chunks:
        raise ValidationError("Document has no indexed content for quiz generation.")

    chunk_texts = [chunk.chunk_text for chunk in chunks]
    context = prepare_quiz_context(chunk_texts)
    questions = _generate_quiz_from_context(
        context,
        count,
        topic=document.filename,
        grade=8,
        source_chunks=chunk_texts,
    )
    payload = _build_response_payload(
        questions,
        SourceType.DOCUMENT,
        count,
        document_id=document_id,
    )
    save_cached_quiz(cache_file, payload)
    logger.info(
        "Generated document quiz: document_id=%d count=%d",
        document_id,
        len(questions),
    )
    return payload


def _format_quiz_questions_for_dyslexia(
    questions: list[dict[str, Any]],
    preserve_terms: set[str],
) -> list[dict[str, Any]]:
    formatted: list[dict[str, Any]] = []
    for question in questions:
        item = dict(question)
        item["question"] = format_text_for_profile(
            question.get("question", ""),
            AccessibilityProfile.DYSLEXIA,
            preserve_terms=preserve_terms,
        )
        for key in ("option_a", "option_b", "option_c", "option_d"):
            item[key] = format_text_for_profile(
                question.get(key, ""),
                AccessibilityProfile.DYSLEXIA,
                preserve_terms=preserve_terms,
            )
        formatted.append(item)
    return formatted


def _apply_accessibility_to_quiz_payload(
    payload: dict[str, Any],
    profile: AccessibilityProfile | None,
    include_audio: bool,
    chunk_texts: list[str] | None = None,
) -> dict[str, Any]:
    if profile is None:
        return payload

    preserve_terms = extract_preserve_terms("\n".join(chunk_texts or []))
    questions = payload.get("questions", [])
    formatted_questions = _format_quiz_questions_for_dyslexia(questions, preserve_terms)
    payload["questions"] = formatted_questions

    audio_source = ". ".join(
        question.get("question", "") for question in formatted_questions[:5]
    )
    payload["accessibility"] = build_accessibility_metadata(
        profile,
        audio_source or payload.get("summary", "Quiz ready."),
        include_audio=include_audio,
    )
    return payload


def generate_quiz(
    source: SourceType,
    db: Session,
    question_count: int | None = None,
    document_id: int | None = None,
    class_level: int | None = None,
    subject: str | None = None,
    chapter: str | None = None,
    topic: str | None = None,
    accessibility_profile: AccessibilityProfile | None = None,
    include_audio: bool = False,
) -> dict[str, Any]:
    """Generate a quiz for Saksham or uploaded document sources."""
    count = clamp_question_count(question_count)
    chapter_ref = chapter or topic

    if source == SourceType.SAKSHAM:
        if class_level is None or not subject or not chapter_ref:
            raise ValidationError(
                "class_level, subject, and chapter are required for saksham quiz."
            )
        payload = generate_saksham_quiz(class_level, subject, chapter_ref, count)
        chunks = get_chapter_chunk_texts(class_level, subject, chapter_ref)
        return _apply_accessibility_to_quiz_payload(
            payload,
            accessibility_profile,
            include_audio,
            chunks,
        )

    if document_id is None:
        raise ValidationError("document_id is required for document quiz.")
    payload = generate_document_quiz(document_id, db, count)
    chunks = [
        chunk.chunk_text
        for chunk in ChunkRepository(db).get_by_document_id(document_id)
    ]
    return _apply_accessibility_to_quiz_payload(
        payload,
        accessibility_profile,
        include_audio,
        chunks,
    )
