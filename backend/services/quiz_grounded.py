"""Generic grounded quiz generation from any chapter or document text."""

from __future__ import annotations

import logging
import re
from typing import Any, Literal

from services.quiz_context import stratified_sample_chunks
from services.quiz_math import _deterministic_shuffle

logger = logging.getLogger(__name__)

QuestionSourceType = Literal["definition", "list", "cloze", "llm"]

_JUNK_SENTENCE = re.compile(
    r"\b("
    r"Reprint|Figure\s+\d|Fig\.\s*\d|Grade\s+\d|"
    r"CHAPTER\s+\d+|Q U E S T I O N S|Happy Exploring|Curiosity \| Textbook|"
    r"Jonali|Pallabi|Example\s+\d|Write the following|"
    r"Let us find|Activity\s+\d|Observe that|"
    r"^\d+\s*$"
    r")\b",
    re.I,
)

_JUNK_TERM = re.compile(
    r"\b(Reprint|Figure|Grade \d|CHAPTER\s+\d|option_[abcd]|Which one of the following|Name one|Enlist the)\b",
    re.I,
)
_EXERCISE_OPTION = re.compile(
    r"\b(Which one of the following|Name one|Enlist the|Specify the|Describe how)\b",
    re.I,
)
_FILLER_OPTION = re.compile(r"^Option\s+\d+$", re.I)
_GARBAGE_TEXT = re.compile(
    r"(.)\1{4,}|[:]{2,}|"
    r"\bV\d+\b|"
    r"\bEq\.?\b|"
    r"\bOption\s+\d+\b|"
    r"\d+\s+\d+\.\d+|"
    r"(?:\b[A-Z]\d+\b\s*){2,}|"
    r"^\d+\s+[A-Z]{4,}"
)
_SECTION_HEADING = re.compile(
    r"^\d+(\.\d+)?\s+[A-Z][A-Z0-9 \-]{5,}$|^\d+\s+\d+\.\d+\s+[A-Z]",
    re.I,
)

_CHAPTER_HEADER = re.compile(
    r"^(?:[A-Z]{2,8}\s+)?(?:The\s+)?[A-Za-z][A-Za-z \-]{3,60}\s+\d+\s*",
    re.I,
)

_IS_CALLED = re.compile(
    r"([^.!?]{12,130}?)\s+is called\s+(?:the\s+)?([^.!?]{3,50}?)(?=\s+and\s+|\s+while\s+|\.|$)",
    re.I,
)
_ARE_CALLED = re.compile(
    r"([^.!?]{8,90}?)\s+are called\s+(?:the\s+)?([^.!?]{3,50}?)(?=\s+while\s+|\.|,|$)",
    re.I,
)
_ALSO_KNOWN_AS = re.compile(
    r"\b([A-Za-z][A-Za-z \-]{2,40}?)\s+is also known as\s+([^.!?]{3,60}?)(?:\.|$)",
    re.I,
)
_IS_KNOWN_AS = re.compile(
    r"([^.!?]{10,100}?)\s+is known as\s+(?:the\s+)?([^.!?]{3,50}?)(?:\.|$)",
    re.I,
)
_LIST_ITEM = re.compile(r"\(\s*([ivx]+|\d+)\s*\)\s*([^,(;.\n]{4,80})", re.I)

_STOPWORDS = frozenset(
    {
        "the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to", "of",
        "and", "or", "for", "with", "by", "from", "as", "that", "this", "it", "its",
        "be", "been", "being", "has", "have", "had", "we", "you", "they", "their",
        "our", "can", "will", "also", "such", "these", "those", "which", "when",
        "where", "who", "whom", "into", "about", "than", "then", "there", "here",
        "very", "each", "all", "both", "not", "only", "may", "one", "two", "three",
    }
)


def _normalize_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.replace("\u2013", "-").replace("\u2014", "-")).strip()
    return re.sub(r"-\s+", "-", cleaned)


def _clean_phrase(text: str) -> str:
    cleaned = _normalize_text(text)
    cleaned = re.sub(r"^\(\w+\)\s*", "", cleaned)
    cleaned = re.sub(r"^\d+\.\d+\s+", "", cleaned)
    cleaned = _CHAPTER_HEADER.sub("", cleaned)
    cleaned = re.sub(r"^[A-Z]{2,8}\s+", "", cleaned)
    return cleaned.strip(" ,;:-")


def _normalize_term(term: str) -> str:
    cleaned = _clean_phrase(term)
    if not cleaned:
        return cleaned
    if cleaned.lower().startswith(("a ", "an ", "the ")):
        return cleaned[0].upper() + cleaned[1:]
    return cleaned[:1].upper() + cleaned[1:]


def _text_in_corpus(text: str, corpus: str) -> bool:
    needle = _normalize_text(text).lower()
    if not needle or len(needle) < 3:
        return False
    return needle in _normalize_text(corpus).lower()


def _attach_meta(
    question: dict[str, Any],
    source_text: str,
    source_type: QuestionSourceType,
) -> dict[str, Any]:
    question["_quiz_meta"] = {
        "source_text": source_text,
        "source_type": source_type,
    }
    return question


def strip_quiz_metadata(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove internal metadata before API/cache output."""
    cleaned: list[dict[str, Any]] = []
    for item in questions:
        cleaned.append({key: value for key, value in item.items() if not key.startswith("_")})
    return cleaned


def _is_usable_definition(subject: str, term: str, is_alias: bool = False) -> bool:
    min_subject_len = 4 if is_alias else 10
    min_subject_words = 1 if is_alias else 3
    if len(subject) < min_subject_len or len(term) < 3:
        return False
    if len(subject) > 120 or len(term) > 70:
        return False
    if _JUNK_TERM.search(subject) or _JUNK_TERM.search(term):
        return False
    if _GARBAGE_TEXT.search(subject) or _GARBAGE_TEXT.search(term):
        return False
    if subject.lower() == term.lower():
        return False
    if not re.match(r"[A-Za-z(]", subject):
        return False
    if len(subject.split()) < min_subject_words:
        return False
    return True


def _is_usable_list_item(text: str) -> bool:
    if len(text) < 15 or len(text.split()) < 3 or len(text) > 80:
        return False
    if text[0] in "])(" or text.endswith("]"):
        return False
    if _JUNK_TERM.search(text) or _EXERCISE_OPTION.search(text):
        return False
    if _GARBAGE_TEXT.search(text):
        return False
    if text.count("?") > 0:
        return False
    if re.match(r"^(in|on|at|to|for|by|of|the|a|an)\s", text, re.I) and len(text.split()) <= 4:
        return False
    return True


def _is_usable_cloze_sentence(sentence: str) -> bool:
    if _SECTION_HEADING.search(sentence.strip()):
        return False
    if _JUNK_SENTENCE.search(sentence):
        return False
    if _GARBAGE_TEXT.search(sentence):
        return False
    if re.search(r"\bEq\.?\b", sentence, re.I):
        return False
    return True


def _question_key(question: str, correct: str = "") -> str:
    base = question.strip().lower()
    if correct:
        return f"{base}|{correct.strip().lower()}"
    return base


def _definition_question_text(subject: str) -> str:
    lowered = subject.lower()
    if lowered.startswith(("a ", "an ", "the ", "if ", "each ", "every ")):
        return f"{subject} is called:"
    return f"What name is given to {subject}?"


_BAD_DISTRACTOR_START = re.compile(
    r"^(?:and|or|but|of|with|by|from|in|on|at|to|for|the|a|an|is|are|was|were|as|than|that|which|who|its|our|your|their|his|her)\b",
    re.I
)
_BAD_DISTRACTOR_END = re.compile(
    r"\b(?:and|or|but|of|with|by|from|in|on|at|to|for|the|a|an|is|are|was|were|as|than|that|which|who|its|our|your|their|his|her|this|these|those)$",
    re.I
)


def _is_usable_distractor(text: str, correct: str = "") -> bool:
    cleaned = text.strip()
    if len(cleaned) < 3 or len(cleaned) > 70:
        return False
    if correct and cleaned.lower() == correct.lower():
        return False
    if _FILLER_OPTION.match(cleaned) or _GARBAGE_TEXT.search(cleaned):
        return False
    if _JUNK_TERM.search(cleaned) or _EXERCISE_OPTION.search(cleaned):
        return False
    if _BAD_DISTRACTOR_START.match(cleaned) or _BAD_DISTRACTOR_END.search(cleaned):
        return False
        
    if correct:
        correct_words = len(correct.split())
        dist_words = len(cleaned.split())
        if correct_words <= 3:
            if dist_words > correct_words + 2 or dist_words < max(1, correct_words - 2):
                return False
        else:
            if dist_words < max(2, correct_words - 3):
                return False
            
    return True


def _pick_distractors(
    correct: str,
    count: int = 3,
    pool: list[str] | None = None,
) -> list[str] | None:
    normalized = _normalize_text(correct).lower()
    candidates = [
        value
        for value in (pool or [])
        if value
        and _is_usable_distractor(value, correct)
        and value.lower() != normalized
        and normalized not in value.lower()
        and value.lower() not in normalized
    ]
    selected: list[str] = []
    for idx in range(len(candidates)):
        if len(selected) >= count:
            break
        candidate = candidates[(hash(normalized) + idx) % len(candidates)]
        if candidate not in selected:
            selected.append(candidate)
    if len(selected) < count:
        return None
    return selected[:count]


def _build_mcq(
    question: str,
    correct: str,
    wrong: tuple[str, ...] | list[str] | None = None,
    pool: list[str] | None = None,
    source_text: str = "",
    source_type: QuestionSourceType = "definition",
) -> dict[str, Any] | None:
    distractors: list[str] | None
    if wrong is not None:
        distractors = list(wrong)
        if any(_FILLER_OPTION.match(value.strip()) for value in distractors):
            return None
    else:
        picked = _pick_distractors(correct, count=3, pool=pool)
        if picked is None:
            return None
        distractors = picked
    if len(distractors) < 3 or len({correct, *distractors[:3]}) < 4:
        return None
    option_values = [correct, *distractors[:3]]
    # Normalize option capitalization matching correct answer
    if correct and correct[0].isupper():
        option_values = [opt[:1].upper() + opt[1:] for opt in option_values]
    else:
        option_values = [opt[:1].lower() + opt[1:] for opt in option_values]
    shuffled, answer = _deterministic_shuffle(option_values, question)
    item = {
        "question": question,
        "options": {
            "A": shuffled[0],
            "B": shuffled[1],
            "C": shuffled[2],
            "D": shuffled[3],
        },
        "correct_answer": answer,
    }
    return _attach_meta(item, source_text or question, source_type)


def _split_sentences(corpus: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", corpus)
    sentences: list[str] = []
    for part in parts:
        cleaned = _clean_phrase(part)
        if 28 <= len(cleaned) <= 240 and "?" not in cleaned:
            if not _JUNK_SENTENCE.search(cleaned) and _is_usable_cloze_sentence(cleaned):
                sentences.append(cleaned)
    return sentences


def _candidate_phrases(sentence: str) -> list[str]:
    words = re.sub(r"[^\w\s\-',]", " ", sentence).split()
    phrases: list[str] = []
    for size in range(min(5, len(words)), 2, -1):
        for start in range(1, max(2, len(words) - size + 1)):
            phrase = " ".join(words[start : start + size]).strip(" ,;:-")
            if len(phrase) < 10 or len(phrase) > 55:
                continue
            tokens = [token.lower() for token in phrase.split()]
            if all(token in _STOPWORDS for token in tokens):
                continue
            if _GARBAGE_TEXT.search(phrase):
                continue
            if _SECTION_HEADING.search(phrase):
                continue
            phrases.append(phrase)
    return phrases


def _collect_definition_terms(corpus: str) -> list[str]:
    """Collect answer terms from definition-style sentences."""
    terms: list[str] = []
    seen: set[str] = set()
    for pattern in (_IS_CALLED, _ARE_CALLED, _IS_KNOWN_AS):
        for match in pattern.finditer(corpus):
            term = _normalize_term(_clean_phrase(match.group(2)))
            key = term.lower()
            if key in seen or not _is_usable_definition(_clean_phrase(match.group(1)), term):
                continue
            seen.add(key)
            terms.append(term)
    for match in _ALSO_KNOWN_AS.finditer(corpus):
        for idx in (1, 2):
            term = _normalize_term(_clean_phrase(match.group(idx)))
            key = term.lower()
            if key in seen:
                continue
            primary = _clean_phrase(match.group(1))
            if not _is_usable_definition(primary, term, is_alias=True):
                continue
            seen.add(key)
            terms.append(term)
    return terms


def _collect_list_items(corpus: str) -> list[str]:
    items: list[str] = []
    seen: set[str] = set()
    for _, text in _LIST_ITEM.findall(corpus):
        item = _clean_phrase(text)
        key = item.lower()
        if key in seen or not _is_usable_list_item(item):
            continue
        seen.add(key)
        items.append(item)
    return items


def _collect_phrase_pool(chunks: list[str]) -> list[str]:
    pool: list[str] = []
    seen: set[str] = set()
    for sentence in _split_sentences("\n".join(chunks)):
        for phrase in _candidate_phrases(sentence):
            key = phrase.lower()
            if key in seen:
                continue
            seen.add(key)
            pool.append(phrase)
    return pool


def _chunk_windows(chunks: list[str], window_size: int = 10) -> list[list[str]]:
    if not chunks:
        return []
    if len(chunks) <= window_size:
        return [chunks]

    windows: list[list[str]] = [chunks]
    step = max(1, (len(chunks) - window_size) // 6)
    for start in range(0, max(1, len(chunks) - window_size + 1), step):
        window = chunks[start : start + window_size]
        if len(window) >= 4:
            windows.append(window)
    windows.append(stratified_sample_chunks(chunks, min(window_size, len(chunks))))
    return windows


def extract_definition_questions(
    chunks: list[str],
    count: int,
    exclude: set[str],
    phrase_pool: list[str],
    definition_term_pool: list[str] | None = None,
    list_item_pool: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Build MCQs from definition-style sentences in chapter text."""
    corpus = "\n".join(chunks)
    definition_terms = definition_term_pool or _collect_definition_terms(corpus)
    list_items = list_item_pool or _collect_list_items(corpus)
    questions: list[dict[str, Any]] = []

    def append(subject: str, term: str, source_text: str, question_text: str | None = None, is_alias: bool = False) -> bool:
        if not _is_usable_definition(subject, term, is_alias=is_alias):
            return False
        qtext = question_text or _definition_question_text(subject)
        correct = _normalize_term(term)
        key = _question_key(qtext, correct)
        if key in exclude:
            return False
        if not _text_in_corpus(correct, source_text):
            return False
        distractor_pool = [value for value in definition_terms if value.lower() != correct.lower()]
        distractor_pool.extend(
            item
            for item in list_items
            if item.lower() != correct.lower()
            and item.lower() not in {value.lower() for value in distractor_pool}
        )
        if len(distractor_pool) < 3:
            distractor_pool.extend(
                phrase
                for phrase in phrase_pool
                if _is_usable_distractor(phrase, correct)
                and phrase.lower() not in {value.lower() for value in distractor_pool}
            )
        if len(distractor_pool) < 3:
            return False
        item = _build_mcq(
            qtext,
            correct,
            pool=distractor_pool,
            source_text=source_text,
            source_type="definition",
        )
        if item is None:
            return False
        questions.append(item)
        return len(questions) >= count

    for pattern in (_IS_CALLED, _ARE_CALLED, _IS_KNOWN_AS):
        for match in pattern.finditer(corpus):
            subject = _clean_phrase(match.group(1))
            term = _clean_phrase(match.group(2))
            source_text = _normalize_text(match.group(0))
            if append(subject, term, source_text):
                return questions[:count]

    for match in _ALSO_KNOWN_AS.finditer(corpus):
        primary = _clean_phrase(match.group(1))
        alias = _clean_phrase(match.group(2))
        source_text = _normalize_text(match.group(0))
        qtext = f"{primary} is also known as:"
        if append(primary, alias, source_text, qtext, is_alias=True):
            return questions[:count]

    return questions[:count]


def extract_list_questions(
    chunks: list[str],
    count: int,
    exclude: set[str],
    phrase_pool: list[str],
) -> list[dict[str, Any]]:
    """Build MCQs from numbered list items in chapter text."""
    questions: list[dict[str, Any]] = []
    for chunk in chunks:
        items = [_clean_phrase(text) for _, text in _LIST_ITEM.findall(chunk)]
        items = [item for item in items if _is_usable_list_item(item)]
        if len(items) < 3:
            continue
        for correct in items[:6]:
            snippet = correct if len(correct) <= 60 else f"{correct[:57]}..."
            question_text = f"Which item from the chapter text matches: \"{snippet}\"?"
            key = _question_key(question_text, correct)
            if key in exclude:
                continue
            wrong_pool = [
                item
                for item in items
                if item != correct and _is_usable_list_item(item)
            ]
            if len(wrong_pool) < 3:
                continue
            wrong = _pick_distractors(correct, count=3, pool=wrong_pool)
            if wrong is None:
                continue
            item = _build_mcq(
                question_text,
                correct,
                wrong=wrong,
                source_text=chunk,
                source_type="list",
            )
            if item is None:
                continue
            questions.append(item)
            if len(questions) >= count:
                return questions[:count]
    return questions[:count]


def extract_sentence_cloze_questions(
    chunks: list[str],
    count: int,
    exclude: set[str],
    phrase_pool: list[str],
) -> list[dict[str, Any]]:
    """Build fill-in-the-blank MCQs from factual chapter sentences."""
    questions: list[dict[str, Any]] = []
    used_phrases: set[str] = set()

    for sentence in _split_sentences("\n".join(chunks)):
        if len(questions) >= count:
            break
        if not _is_usable_cloze_sentence(sentence):
            continue
        for phrase in _candidate_phrases(sentence):
            phrase_key = phrase.lower()
            if phrase_key in used_phrases:
                continue
            start_idx = sentence.lower().find(phrase.lower())
            if start_idx < 0:
                continue
            if start_idx > 0 and sentence[start_idx - 1].isalnum():
                continue
            prefix = sentence[:start_idx].rstrip()
            if re.search(r"\b[A-Z]$", prefix):
                continue
            if not _text_in_corpus(phrase, sentence):
                continue
            blanked = re.sub(re.escape(phrase), "______", sentence, count=1, flags=re.I)
            if blanked == sentence or blanked.startswith("______"):
                continue
            if re.search(r"\b[A-Z]\s+______", blanked):
                continue
            if re.search(r"\b[A-Z]\s+[a-z]+\s+\S*\s*______", blanked):
                continue
            question_text = f"Complete the statement: {blanked}"
            if len(question_text) > 220:
                continue
            key = _question_key(question_text, phrase)
            if key in exclude:
                continue
            wrong = _pick_distractors(
                phrase,
                count=3,
                pool=[
                    p
                    for p in phrase_pool
                    if _is_usable_distractor(p, phrase)
                ],
            )
            if wrong is None:
                continue
            item = _build_mcq(
                question_text,
                phrase,
                wrong=wrong,
                source_text=sentence,
                source_type="cloze",
            )
            if item is None:
                continue
            used_phrases.add(phrase_key)
            questions.append(item)
            break

    return questions[:count]


def is_valid_grounded_question(
    question: str,
    options: dict[str, str],
    is_cloze: bool = False,
    correct_answer: str | None = None,
) -> bool:
    """Reject malformed or low-quality grounded MCQs.
    
    Args:
        question: The question text.
        options: Dict mapping option letter (A-D) to text.
        is_cloze: Whether this is a fill-in-the-blank cloze question.
        correct_answer: The correct answer text. If provided, the verbatim
            overlap check applies only to this answer, not all distractors.
    """
    cleaned = question.strip()
    if len(cleaned) < 12 or len(cleaned) > 220:
        logger.info("is_valid_grounded_question rejected: length check failed (%d chars)", len(cleaned))
        return False
    if _JUNK_SENTENCE.search(cleaned):
        logger.info("is_valid_grounded_question rejected: junk sentence pattern matched")
        return False
    if cleaned.count("?") > 1:
        logger.info("is_valid_grounded_question rejected: multiple question marks")
        return False
    values = [value.strip() for value in options.values()]
    if not all(values) or len(set(values)) < 4:
        logger.info("is_valid_grounded_question rejected: duplicate or empty options")
        return False
    if any(len(value) < 3 or len(value) > 90 for value in values):
        logger.info("is_valid_grounded_question rejected: option too short or too long")
        return False
    if any(_FILLER_OPTION.match(value) for value in values):
        logger.info("is_valid_grounded_question rejected: filler option matched")
        return False
    if any(_EXERCISE_OPTION.search(value) for value in values):
        logger.info("is_valid_grounded_question rejected: exercise option matched")
        return False
    if any(_GARBAGE_TEXT.search(value) for value in values):
        logger.info("is_valid_grounded_question rejected: garbage text matched")
        return False
    for value in values:
        if value.endswith("?") or value.lower().startswith(("what ", "who ", "where ", "why ", "when ", "how ", "which ")):
            logger.info("is_valid_grounded_question rejected: option format looks like a question: %s", value)
            return False

    # 1. Reject if the CORRECT answer is present verbatim inside the question (answer leak).
    # Only the correct answer is checked — checking distractors caused false rejections because
    # distractors legitimately contain words that appear in the question stem.
    if not is_cloze:
        question_lower = cleaned.lower()
        check_text = correct_answer if correct_answer is not None else None
        if check_text is not None:
            val_lower = check_text.strip().lower()
            if len(val_lower) > 4:
                if val_lower in question_lower or question_lower in val_lower:
                    logger.info(
                        "is_valid_grounded_question rejected: correct answer verbatim inside question: %s",
                        check_text,
                    )
                    return False

    # 2. Reject statement-matching or text recognition patterns (unless it is a heuristic cloze question)
    if not is_cloze:
        question_lower = cleaned.lower()
        bad_patterns = [
            "matches:",
            "matches \"",
            "which item",
            "which statement",
            "complete the statement",
            "complete the sentence",
            "fill in the blank",
            "blanked",
            "______",
            "notice ",
            "the terrain here",
            "notice the",
            "Notice that"
        ]
        for pattern in bad_patterns:
            if pattern in question_lower:
                logger.info("is_valid_grounded_question rejected: bad pattern matched: %s", pattern)
                return False

    # 3. Reject weak filler options (like "all of the above", "both a and b")
    meta_option_pat = re.compile(
        r"\b(?:all of the above|none of the above|both [a-d] and [a-d]|all of these|none of these|above options|neither [a-d] nor [a-d]|\ball of the these)\b",
        re.I
    )
    if any(meta_option_pat.search(value) for value in values):
        logger.info("is_valid_grounded_question rejected: meta/filler option pattern matched")
        return False

    return True


def verify_grounded_question(item: dict[str, Any], corpus: str) -> bool:
    """Verify a grounded MCQ against chapter source text."""
    question = str(item.get("question", "")).strip()
    options = item.get("options", {})
    if not isinstance(options, dict):
        return False
    meta = item.get("_quiz_meta", {})
    source_type = str(meta.get("source_type", ""))
    is_cloze = (source_type == "cloze")

    answer_key = str(item.get("correct_answer", "")).strip().upper()
    if answer_key not in options:
        return False
    correct_text = str(options[answer_key]).strip()

    if not is_valid_grounded_question(question, options, is_cloze=is_cloze, correct_answer=correct_text):
        return False

    if _FILLER_OPTION.match(correct_text) or _GARBAGE_TEXT.search(correct_text):
        return False

    source_text = str(meta.get("source_text", ""))


    if source_type == "cloze":
        if not source_text or not _text_in_corpus(correct_text, source_text):
            return False
        if _SECTION_HEADING.search(correct_text):
            return False
    elif source_type in {"definition", "list"}:
        anchor = source_text or correct_text
        if not _text_in_corpus(correct_text, anchor) and not _text_in_corpus(correct_text, corpus):
            return False
    elif source_type == "llm":
        if not verify_llm_question(item, corpus):
            return False
    else:
        if not _text_in_corpus(correct_text, corpus):
            return False

    return True


def verify_llm_question(item: dict[str, Any], corpus: str) -> bool:
    """Factual/reasoning verification for LLM-generated MCQs using local LLM solver."""
    question = str(item.get("question", "")).strip()
    if "?" not in question:
        return False
    options = item.get("options", {})
    if not isinstance(options, dict):
        return False

    answer_key = str(item.get("correct_answer", "")).strip().upper()
    if answer_key not in options:
        return False
    correct_text = str(options[answer_key]).strip()

    if not is_valid_grounded_question(question, options, is_cloze=False, correct_answer=correct_text):
        return False

    if _FILLER_OPTION.match(correct_text) or _GARBAGE_TEXT.search(correct_text):
        return False

    # Fast Python verification: Check if the correct answer matches/overlaps with the corpus
    if _text_in_corpus(correct_text, corpus):
        return True
        
    local_stopwords = _STOPWORDS.union({
        "because", "since", "why", "how", "what", "who", "where", "when", 
        "if", "should", "could", "would", "did", "does", "do", "done", 
        "make", "makes", "making", "have", "has", "having", "do", "does", 
        "doing", "get", "gets", "getting", "go", "goes", "going", "want", 
        "wants", "need", "needs", "called", "known", "means", "about", 
        "other", "some", "many", "more", "most", "also", "only", "such",
        "about", "their", "them", "they", "there", "these", "those"
    })
    
    tokens = [t for t in re.findall(r"[a-z]{4,}", correct_text.lower())]
    tokens = [t for t in tokens if t not in local_stopwords]
    if tokens and any(t in corpus.lower() for t in tokens):
        return True

    from ai.llm import get_llm, OllamaLLM
    from ai.prompt_builder import build_solve_prompt
    
    llm = get_llm()
    # Bypass for unit tests that use MockLLM or other mock clients
    if not isinstance(llm, OllamaLLM):
        return False

    # Production flow: Retrieve best context and solve
    def find_best_context(q: str, opts: dict[str, str], corp: str) -> str:
        paragraphs = [p.strip() for p in corp.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [p.strip() for p in corp.split("\n") if p.strip()]
        if not paragraphs:
            return corp[:4000]
            
        blocks = []
        curr_block = []
        curr_len = 0
        for p in paragraphs:
            if curr_len + len(p) > 3000:
                if curr_block:
                    blocks.append("\n\n".join(curr_block))
                curr_block = [p]
                curr_len = len(p)
            else:
                curr_block.append(p)
                curr_len += len(p) + 2
        if curr_block:
            blocks.append("\n\n".join(curr_block))
            
        best_block = blocks[0] if blocks else corp[:3000]
        best_score = -1
        
        q_words = set(re.findall(r"\w+", q.lower()))
        for opt in opts.values():
            q_words.update(re.findall(r"\w+", opt.lower()))
        q_words = {w for w in q_words if w not in _STOPWORDS and len(w) > 2}
        
        for block in blocks:
            block_lower = block.lower()
            score = sum(1 for w in q_words if w in block_lower)
            if score > best_score:
                best_score = score
                best_block = block
        return best_block

    context = find_best_context(question, options, corpus)
    prompt = build_solve_prompt(context, question, options)
    response = llm.generate(prompt, num_predict=16)
    
    solved_text = response.strip()
    # Normalize to uppercase for matching, but keep original for logging
    solved_upper = solved_text.upper()

    # Strategy 1: Response starts directly with the option letter (ideal output from SOLVER_SYSTEM_PROMPT)
    # e.g. "B", "B.", "B:", "B)"
    direct_match = re.match(r"^([ABCD])[.:\)\s]?$", solved_upper)
    if direct_match:
        solved_option = direct_match.group(1)
        if solved_option == answer_key:
            return True
        logger.info(
            "verify_llm_question rejected: solver selected '%s' but correct_answer is '%s' (question: '%s')",
            solved_option, answer_key, question,
        )
        return False

    # Strategy 2: Response contains explicit prefix patterns
    # e.g. "CORRECT OPTION: B", "ANSWER IS B", "THE CORRECT ANSWER IS B"
    prefix_match = re.search(
        r"(?:CORRECT OPTION|CORRECT ANSWER|ANSWER IS|THE ANSWER IS)[:\s]+([ABCD]|NONE)\b",
        solved_upper,
    )
    if prefix_match:
        solved_option = prefix_match.group(1)
        if solved_option == "NONE":
            logger.info("verify_llm_question rejected: solver returned NONE (question: '%s')", question)
            return False
        if solved_option == answer_key:
            return True
        logger.info(
            "verify_llm_question rejected: solver selected '%s' but correct_answer is '%s' (question: '%s')",
            solved_option, answer_key, question,
        )
        return False

    # Strategy 3: Short responses only (<=10 chars) — search for a standalone letter.
    # We intentionally skip this for long prose responses to avoid the letter 'a' (article)
    # being matched as option A in sentences like "This was not found in a chapter".
    if len(solved_text) <= 10:
        letter_match = re.search(r"\b([ABCD]|NONE)\b", solved_upper)
        if letter_match:
            solved_option = letter_match.group(1)
            if solved_option == "NONE":
                logger.info("verify_llm_question rejected: solver returned NONE (question: '%s')", question)
                return False
            if solved_option == answer_key:
                return True
            logger.info(
                "verify_llm_question rejected: solver selected '%s' but correct_answer is '%s' (question: '%s')",
                solved_option, answer_key, question,
            )
            return False

    logger.info(
        "verify_llm_question rejected: solver output not parseable. Response: '%s' (question: '%s')",
        solved_text[:120], question,
    )
    return False


def filter_grounded_questions(
    questions: list[dict[str, Any]],
    corpus: str = "",
) -> list[dict[str, Any]]:
    """Keep only verified grounded MCQs."""
    filtered: list[dict[str, Any]] = []
    for item in questions:
        if verify_grounded_question(item, corpus):
            filtered.append(item)
    return filtered


def build_grounded_chapter_questions(
    chunks: list[str],
    count: int,
    chapter_title: str = "",
    exclude_questions: list[dict[str, Any]] | None = None,
    allow_cloze: bool = True,
) -> list[dict[str, Any]]:
    """
    Build factual MCQs from chapter text using tiered, verified extractors.

    Priority: definitions → list items → sentence cloze (strict, optional).
    """
    if not chunks or count <= 0:
        return []

    corpus = "\n".join(chunks)
    seen: set[str] = set()
    for item in exclude_questions or []:
        question = str(item.get("question", "")).strip()
        correct = ""
        options = item.get("options", {})
        answer = str(item.get("correct_answer", "")).strip().upper()
        if isinstance(options, dict) and answer in options:
            correct = str(options[answer])
        if question:
            seen.add(_question_key(question, correct))

    questions: list[dict[str, Any]] = []
    definition_terms = _collect_definition_terms(corpus)
    list_items = _collect_list_items(corpus)

    def accept(batch: list[dict[str, Any]]) -> None:
        nonlocal questions
        for item in filter_grounded_questions(batch, corpus):
            correct = item["options"][item["correct_answer"]]
            key = _question_key(item["question"], correct)
            if key in seen:
                continue
            seen.add(key)
            questions.append(item)
            if len(questions) >= count:
                return

    for window in _chunk_windows(chunks):
        phrase_pool = _collect_phrase_pool(window)
        needed = count - len(questions)
        if needed <= 0:
            break
        accept(
            extract_definition_questions(
                window,
                needed * 2,
                seen,
                phrase_pool,
                definition_term_pool=definition_terms,
                list_item_pool=list_items,
            )
        )
        # Skip list matching questions to avoid low-quality identity-matching MCQs.
        # accept(extract_list_questions(window, needed * 2, seen, phrase_pool))

    if allow_cloze and len(questions) < count:
        for window in _chunk_windows(chunks):
            needed = count - len(questions)
            if needed <= 0:
                break
            phrase_pool = _collect_phrase_pool(window)
            accept(extract_sentence_cloze_questions(window, needed * 2, seen, phrase_pool))

    return questions[:count]


def tag_llm_questions(questions: list[dict[str, Any]], corpus: str) -> list[dict[str, Any]]:
    """Attach LLM source metadata for downstream verification."""
    tagged: list[dict[str, Any]] = []
    for item in questions:
        copy = dict(item)
        copy["_quiz_meta"] = {"source_text": corpus[:2000], "source_type": "llm"}
        tagged.append(copy)
    return tagged
