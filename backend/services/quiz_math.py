"""Math-specific quiz helpers: fact extraction, templates, and quality checks."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

_MATH_SUBJECTS = frozenset({"mathematics", "maths", "math"})

_MUL_PATTERN = re.compile(
    r"(?P<a>\d+(?:\.\d+)?)\s*[×x*]\s*(?P<b>\d+(?:\.\d+)?)\s*=\s*(?P<c>\d+(?:\.\d+)?)"
)
_DIV_PATTERN = re.compile(
    r"(?P<a>\d+(?:\.\d+)?)\s*÷\s*(?P<b>\d+(?:\.\d+)?)\s*=\s*(?P<c>\d+(?:\.\d+)?)"
)
_ADD_SUB_PATTERN = re.compile(
    r"(?P<a>\d+(?:\.\d+)?)\s*(?P<op>[+\-])\s*(?P<b>\d+(?:\.\d+)?)\s*=\s*(?P<c>\d+(?:\.\d+)?)"
)

_NARRATIVE_QUESTION = re.compile(
    r"\b("
    r"Jonali|Pallabi|Arshad|Ajay|Ganita Prakash|play a game|blank spaces|"
    r"Write the following|Answer in kilometres|Math Talk|Grade 7 \| Part"
    r")\b",
    re.I,
)
_EXAMPLE_PREFIX = re.compile(r"^\s*Example\s+\d+\s*:", re.I)
_INSTRUCTION_PREFIX = re.compile(
    r"^\s*(Write|Construct|Find the area of the given|Suppose we know that|Can the product)\b",
    re.I,
)

_CONCEPT_CHUNK = re.compile(
    r"\b(decimal|place value|multiply|divide|fraction|tenth|hundredth|product|numerator)\b",
    re.I,
)
_GEOMETRY_QUESTION = re.compile(
    r"\b(triangle|equilateral|isosceles|vertices|vertex|side lengths|side length)\b",
    re.I,
)
_EXPRESSION_QUESTION = re.compile(
    r"\b(expression|evaluate|value of|bodmas|bracket)\b",
    re.I,
)

_MATH_CHAPTER_KINDS = frozenset({"geometry", "expressions", "decimals", "arithmetic"})

_SIDE_TRIPLE_PATTERNS = (
    (re.compile(r"\(\s*[a-z]\s*\)\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", re.I), "cm"),
    (re.compile(r"lengths\s+(\d+)\s*cm,\s*(\d+)\s*cm\s+and\s+(\d+)\s*cm", re.I), "cm"),
    (re.compile(r"(\d+)\s*km,\s*(\d+)\s*km\s+and\s*(\d+)\s*km", re.I), "km"),
    (re.compile(r"(\d+)\s*mm,\s*(\d+)\s*mm\s+and\s*(\d+)\s*mm", re.I), "mm"),
)

_DEFINITION_TEMPLATES: tuple[dict[str, Any], ...] = (
    {
        "kinds": frozenset({"geometry"}),
        "keywords": ("vertex", "vertices", "triangle"),
        "question": "How many vertices does a triangle have?",
        "correct": "3",
        "wrong": ("2", "4", "6"),
    },
    {
        "kinds": frozenset({"geometry"}),
        "keywords": ("equilateral",),
        "question": "How many equal sides does an equilateral triangle have?",
        "correct": "3",
        "wrong": ("1", "2", "4"),
    },
    {
        "kinds": frozenset({"geometry"}),
        "keywords": ("isosceles",),
        "question": "How many equal sides does an isosceles triangle have?",
        "correct": "2",
        "wrong": ("1", "3", "4"),
    },
    {
        "kinds": frozenset({"geometry"}),
        "keywords": ("180",),
        "required": ("triangle",),
        "question": "What is the sum of the three angles of a triangle?",
        "correct": "180°",
        "wrong": ("90°", "360°", "270°"),
    },
    {
        "kinds": frozenset({"expressions"}),
        "keywords": ("arithmetic expression", "expression has a value"),
        "question": "What is an arithmetic expression?",
        "correct": "A mathematical phrase that evaluates to a number",
        "wrong": (
            "A geometric shape with three sides",
            "A word problem about daily life",
            "An unknown value called x",
        ),
    },
    {
        "kinds": frozenset({"expressions"}),
        "keywords": ("equality sign", "value of the expression"),
        "question": "In 13 + 2 = 15, what does the '=' sign show?",
        "correct": "The value of the expression",
        "wrong": (
            "The next example in the chapter",
            "That the numbers are unequal",
            "The chapter title",
        ),
    },
)


@dataclass(frozen=True)
class SideTriple:
    """Three side lengths mentioned in the chapter text."""

    a: int
    b: int
    c: int
    unit: str = "cm"


@dataclass(frozen=True)
class MathFact:
    """A validated arithmetic fact extracted from chapter text."""

    operator: str
    left: float
    right: float
    result: float
    source: str


def _triangle_exists(a: int, b: int, c: int) -> bool:
    sides = sorted((a, b, c))
    return sides[0] + sides[1] > sides[2]


def extract_side_triples(chunks: list[str], max_side: int = 200) -> list[SideTriple]:
    """Extract side-length triples used in triangle-inequality discussions."""
    seen: set[tuple[int, int, int]] = set()
    triples: list[SideTriple] = []

    for chunk in chunks:
        for pattern, unit in _SIDE_TRIPLE_PATTERNS:
            for match in pattern.finditer(chunk):
                a, b, c = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
                if min(a, b, c) <= 0 or max(a, b, c) > max_side:
                    continue
                key = tuple(sorted((a, b, c)))
                if key in seen:
                    continue
                seen.add(key)
                triples.append(SideTriple(a=a, b=b, c=c, unit=unit))
    return triples


def build_triangle_inequality_questions(
    triples: list[SideTriple],
    count: int,
) -> list[dict[str, Any]]:
    """Build MCQs testing whether three side lengths can form a triangle."""
    questions: list[dict[str, Any]] = []
    for triple in triples:
        if len(questions) >= count:
            break
        exists = _triangle_exists(triple.a, triple.b, triple.c)
        question_text = (
            f"Can a triangle have side lengths {triple.a} {triple.unit}, "
            f"{triple.b} {triple.unit}, and {triple.c} {triple.unit}?"
        )
        if exists:
            correct = "Yes, a triangle is possible"
            wrong = (
                "No, a triangle is not possible",
                "Only if all three sides are equal",
                "Only if two sides are equal",
            )
        else:
            correct = "No, a triangle is not possible"
            wrong = (
                "Yes, a triangle is possible",
                "Yes, when two sides are equal",
                "Yes, when the longest side equals the sum of the other two",
            )

        option_values = [correct, *wrong]
        shuffled, answer = _deterministic_shuffle(option_values, question_text)
        questions.append(
            {
                "question": question_text,
                "options": {
                    "A": shuffled[0],
                    "B": shuffled[1],
                    "C": shuffled[2],
                    "D": shuffled[3],
                },
                "correct_answer": answer,
            }
        )
    return questions


def detect_math_chapter_kind(chunks: list[str], chapter_title: str = "") -> str:
    """Classify a math chapter so quiz templates match the topic."""
    title = chapter_title.lower()
    corpus = f"{chapter_title}\n" + "\n".join(chunks).lower()

    if any(
        token in title
        for token in ("triangle", "intersecting lines", "circle", "symmetry", "quadrilateral")
    ):
        return "geometry"
    if any(token in title for token in ("expression", "bodmas", "integer")):
        return "expressions"
    if any(token in title for token in ("decimal", "fraction")):
        return "decimals"

    scores = {
        "geometry": sum(
            1
            for keyword in (
                "triangle",
                "equilateral",
                "isosceles",
                "side lengths",
                "intersecting lines",
            )
            if keyword in corpus
        ),
        "expressions": sum(
            1
            for keyword in (
                "arithmetic expression",
                "value of the expression",
                "equality sign",
                "bodmas",
                "bracket",
            )
            if keyword in corpus
        ),
        "decimals": sum(
            1
            for keyword in ("decimal", "tenth", "hundredth", "place value")
            if keyword in corpus
        ),
    }
    best_kind = max(scores, key=scores.get)
    if scores[best_kind] >= 2:
        return best_kind
    return "arithmetic"


def _template_matches(corpus: str, template: dict[str, Any], chapter_kind: str) -> bool:
    if chapter_kind not in template["kinds"]:
        return False
    if not any(keyword in corpus for keyword in template["keywords"]):
        return False
    required = template.get("required", ())
    return all(keyword in corpus for keyword in required)


def build_definition_questions(
    chunks: list[str],
    count: int,
    chapter_kind: str,
) -> list[dict[str, Any]]:
    """Build definition MCQs scoped to the detected chapter topic."""
    corpus = "\n".join(chunks).lower()
    questions: list[dict[str, Any]] = []
    for template in _DEFINITION_TEMPLATES:
        if len(questions) >= count:
            break
        if not _template_matches(corpus, template, chapter_kind):
            continue
        question_text = template["question"]
        option_values = [template["correct"], *template["wrong"]]
        shuffled, answer = _deterministic_shuffle(option_values, question_text)
        questions.append(
            {
                "question": question_text,
                "options": {
                    "A": shuffled[0],
                    "B": shuffled[1],
                    "C": shuffled[2],
                    "D": shuffled[3],
                },
                "correct_answer": answer,
            }
        )
    return questions


def build_concept_questions(
    chunks: list[str],
    count: int,
    chapter_kind: str,
) -> list[dict[str, Any]]:
    """Build geometry/concept MCQs for geometry chapters only."""
    if count <= 0 or chapter_kind != "geometry":
        return []

    triples = extract_side_triples(chunks)
    questions = build_triangle_inequality_questions(triples, count)
    if len(questions) >= count:
        return questions[:count]

    remaining = count - len(questions)
    questions.extend(build_definition_questions(chunks, remaining, chapter_kind))
    return questions[:count]


def build_chapter_quiz_questions(
    chunks: list[str],
    count: int,
    chapter_title: str = "",
) -> tuple[list[dict[str, Any]], str]:
    """Build topic-aligned math MCQs from chapter content."""
    chapter_kind = detect_math_chapter_kind(chunks, chapter_title)
    questions: list[dict[str, Any]] = []

    if chapter_kind == "geometry":
        questions.extend(build_concept_questions(chunks, count, chapter_kind))
        remaining = max(0, count - len(questions))
        if remaining > 0:
            facts = _prioritize_facts(extract_valid_math_facts(chunks), chapter_kind)
            questions.extend(build_fact_questions(facts, remaining, chapter_kind=chapter_kind))
    else:
        facts = _prioritize_facts(extract_valid_math_facts(chunks), chapter_kind)
        questions.extend(build_fact_questions(facts, count, chapter_kind=chapter_kind))
        remaining = max(0, count - len(questions))
        if remaining > 0:
            questions.extend(build_definition_questions(chunks, remaining, chapter_kind))

    remaining = max(0, count - len(questions))
    if remaining > 0 and chapter_kind == "geometry":
        questions.extend(build_definition_questions(chunks, remaining, chapter_kind))

    return questions[:count], chapter_kind


def is_math_subject(subject: str | None) -> bool:
    """Return True when the subject is a mathematics course."""
    if not subject:
        return False
    return subject.strip().lower() in _MATH_SUBJECTS


def _approx_equal(left: float, right: float, tolerance: float = 0.02) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def _format_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    text = f"{value:g}"
    return text


def extract_valid_math_facts(chunks: list[str]) -> list[MathFact]:
    """Extract numerically valid arithmetic facts from chapter chunks."""
    seen: set[tuple[str, float, float, float]] = set()
    facts: list[MathFact] = []

    for chunk in chunks:
        normalized = re.sub(r"\s+", " ", chunk)
        for match in _ADD_SUB_PATTERN.finditer(normalized):
            left = float(match.group("a"))
            operator = match.group("op")
            right = float(match.group("b"))
            result = float(match.group("c"))
            if operator == "+":
                if not _approx_equal(left + right, result):
                    continue
            elif not _approx_equal(left - right, result):
                continue
            key = (operator, left, right, result)
            if key in seen:
                continue
            seen.add(key)
            facts.append(
                MathFact(
                    operator=operator,
                    left=left,
                    right=right,
                    result=result,
                    source=match.group(0),
                )
            )

        for pattern, operator in ((_DIV_PATTERN, "÷"), (_MUL_PATTERN, "×")):
            for match in pattern.finditer(normalized):
                left = float(match.group("a"))
                right = float(match.group("b"))
                result = float(match.group("c"))
                if operator == "÷":
                    if right == 0 or not _approx_equal(left / right, result):
                        continue
                elif not _approx_equal(left * right, result):
                    continue

                key = (operator, left, right, result)
                if key in seen:
                    continue
                seen.add(key)
                facts.append(
                    MathFact(
                        operator=operator,
                        left=left,
                        right=right,
                        result=result,
                        source=match.group(0),
                    )
                )
    return facts


def _fact_complexity(fact: MathFact) -> float:
    return abs(fact.left) + abs(fact.right) + abs(fact.result)


def _prioritize_facts(facts: list[MathFact], chapter_kind: str) -> list[MathFact]:
    if chapter_kind == "expressions":
        return sorted(facts, key=_fact_complexity, reverse=True)
    return facts


def _format_expression_text(fact: MathFact) -> str:
    if fact.operator == "-":
        symbol = "−"
    else:
        symbol = fact.operator
    return f"{_format_number(fact.left)} {symbol} {_format_number(fact.right)}"


def _question_text_for_fact(fact: MathFact, chapter_kind: str) -> str:
    if chapter_kind == "expressions":
        return f"What is the value of the expression {_format_expression_text(fact)}?"
    if fact.operator == "÷":
        return f"What is {_format_number(fact.left)} ÷ {_format_number(fact.right)}?"
    if fact.operator == "×":
        return f"What is {_format_number(fact.left)} × {_format_number(fact.right)}?"
    if fact.operator == "+":
        return f"What is {_format_number(fact.left)} + {_format_number(fact.right)}?"
    return f"What is {_format_number(fact.left)} − {_format_number(fact.right)}?"


def is_narrative_math_chunk(text: str) -> bool:
    """Detect story/exercise-setup chunks that produce poor math quizzes."""
    cleaned = text.strip()
    if not cleaned:
        return True
    equation_count = len(_MUL_PATTERN.findall(cleaned)) + len(_DIV_PATTERN.findall(cleaned))
    if equation_count >= 2:
        return False
    if _NARRATIVE_QUESTION.search(cleaned):
        return True
    if cleaned.count("?") >= 3 and _INSTRUCTION_PREFIX.search(cleaned):
        return True
    return False


def filter_math_quiz_chunks(chunks: list[str]) -> list[str]:
    """Keep concept and worked-example chunks; drop story/exercise setup."""
    filtered: list[str] = []
    for chunk in chunks:
        if not chunk or not chunk.strip():
            continue
        if is_narrative_math_chunk(chunk):
            continue
        filtered.append(chunk.strip())

    if filtered:
        return filtered

    concept_chunks = [chunk.strip() for chunk in chunks if chunk.strip() and _CONCEPT_CHUNK.search(chunk)]
    return concept_chunks or [chunk.strip() for chunk in chunks if chunk.strip()]


def format_math_facts_for_prompt(facts: list[MathFact], limit: int = 12) -> str:
    """Format extracted facts as compact reference lines for the LLM."""
    lines = []
    for fact in facts[:limit]:
        lines.append(
            f"- {_format_number(fact.left)} {fact.operator} "
            f"{_format_number(fact.right)} = {_format_number(fact.result)}"
        )
    return "\n".join(lines)


def _deterministic_shuffle(options: list[str], seed_text: str) -> tuple[list[str], str]:
    """Shuffle options deterministically and return the correct answer letter."""
    correct = options[0]
    ordered = options[:]
    digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    for index in range(len(ordered) - 1, 0, -1):
        swap_with = int(digest[index % len(digest) : index % len(digest) + 2], 16) % (index + 1)
        ordered[index], ordered[swap_with] = ordered[swap_with], ordered[index]
    correct_index = ordered.index(correct)
    letter = "ABCD"[correct_index]
    return ordered, letter


def _make_numeric_distractors(correct: float, operator: str) -> list[str]:
    """Build plausible wrong numeric options."""
    candidates = [
        correct * 10,
        correct / 10 if correct else 0.1,
        correct * 2,
        correct + 1,
        correct - 0.1 if correct > 0.1 else correct + 0.5,
    ]
    if operator == "÷":
        candidates.extend([correct * 100, correct + 10])
    else:
        candidates.extend([correct / 100 if correct else 0.01, correct + 5])

    distractors: list[str] = []
    correct_text = _format_number(correct)
    for candidate in candidates:
        text = _format_number(candidate)
        if text == correct_text or text in distractors:
            continue
        distractors.append(text)
        if len(distractors) == 3:
            break

    fallback = ["0.1", "1", "10", "100", "0.01", "2", "5"]
    for value in fallback:
        if len(distractors) >= 3:
            break
        if value != correct_text and value not in distractors:
            distractors.append(value)
    return distractors[:3]


def build_fact_questions(
    facts: list[MathFact],
    count: int,
    chapter_kind: str = "arithmetic",
) -> list[dict[str, Any]]:
    """Build grounded MCQs directly from validated chapter arithmetic facts."""
    questions: list[dict[str, Any]] = []
    for fact in facts:
        if len(questions) >= count:
            break
        question_text = _question_text_for_fact(fact, chapter_kind)
        correct_text = _format_number(fact.result)
        option_values = [correct_text, *_make_numeric_distractors(fact.result, fact.operator)]
        shuffled, answer = _deterministic_shuffle(option_values[:4], question_text)
        questions.append(
            {
                "question": question_text,
                "options": {
                    "A": shuffled[0],
                    "B": shuffled[1],
                    "C": shuffled[2],
                    "D": shuffled[3],
                },
                "correct_answer": answer,
            }
        )
    return questions


def is_valid_math_question(question: str, options: dict[str, str]) -> bool:
    """Reject story/exercise-copy questions and weak option sets."""
    cleaned = question.strip()
    if len(cleaned) < 12 or len(cleaned) > 160:
        return False
    if _NARRATIVE_QUESTION.search(cleaned):
        return False
    if _EXAMPLE_PREFIX.search(cleaned):
        return False
    if _INSTRUCTION_PREFIX.search(cleaned):
        return False
    if cleaned.count("?") > 1:
        return False

    values = [value.strip() for value in options.values()]
    if not all(values) or len(set(values)) < 4:
        return False
    if not re.search(r"\d", cleaned) and not _CONCEPT_CHUNK.search(cleaned):
        if not _GEOMETRY_QUESTION.search(cleaned) and not _EXPRESSION_QUESTION.search(cleaned):
            return False
    return True


def filter_math_questions(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only high-quality math MCQs."""
    filtered: list[dict[str, Any]] = []
    for item in questions:
        question = str(item.get("question", "")).strip()
        options = item.get("options", {})
        if not isinstance(options, dict):
            continue
        if not is_valid_math_question(question, options):
            continue
        filtered.append(item)
    return filtered
