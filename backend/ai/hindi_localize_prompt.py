"""Prompt templates for English-to-Hinenglish localization (no RAG)."""

from __future__ import annotations

from config.constants import LocalizeContentType

HINDI_LOCALIZE_MARKER = "HINDI_LOCALIZE_PROMPT"

_COMMON_RULES = """
Rules:
- Write explanatory prose in Devanagari (Hindi script).
- Do NOT add or remove facts. Translate/paraphrase ONLY the given English text.
- Keep unchanged: proper nouns (e.g. Louis XVI), numbers, formulas (H2O), units (cm, Newton), MCQ letters (A/B/C/D).
- For science terms use: Hindi explanation (English term) on first mention, e.g. प्रकाश संश्लेषण (Photosynthesis).
- If a word has no simple Hindi equivalent, keep the English word.
- Preserve bullet structure (•) and paragraph breaks.
- Do NOT answer in English only.
""".strip()

_STRICT_RETRY_SUFFIX = """
CRITICAL: Your previous attempt failed validation. Output MUST be mostly Devanagari Hindi.
Keep English only for proper nouns, formulas, and technical terms in brackets.
""".strip()


def _class_hint(class_level: int | None) -> str:
    if class_level is None:
        return "Use simple school-level Hindi."
    if class_level <= 8:
        return f"Use very simple Hindi suitable for Class {class_level} students."
    return f"Use clear Hindi suitable for Class {class_level} students."


def _preserve_terms_block(preserve_terms: list[str] | None) -> str:
    if not preserve_terms:
        return ""
    terms = ", ".join(dict.fromkeys(term.strip() for term in preserve_terms if term.strip()))
    if not terms:
        return ""
    return f"\nPreserve these terms exactly when they appear: {terms}\n"


def build_prose_localize_prompt(
    english_text: str,
    content_type: LocalizeContentType,
    *,
    class_level: int | None = None,
    preserve_terms: list[str] | None = None,
    strict_retry: bool = False,
) -> str:
    """Build prompt to convert English answer/summary/simplify text to Hinenglish."""
    type_label = {
        LocalizeContentType.ANSWER: "student answer",
        LocalizeContentType.SUMMARY: "chapter summary",
        LocalizeContentType.SIMPLIFY: "simplified explanation",
    }[content_type]

    retry_block = f"\n{_STRICT_RETRY_SUFFIX}\n" if strict_retry else ""
    return f"""{HINDI_LOCALIZE_MARKER}

Convert the following English {type_label} into Hinenglish for Indian school students.

Use very simple Hindi suitable for Class {class_level} students.

Rules:
- Write explanatory prose in Devanagari (Hindi script).
- Keep technical terms unchanged in brackets: e.g. प्रकाश (Light), परावर्तन (Reflection).
- Do NOT mix English and Hindi letters in a single word (e.g. write "बाउंस" or "bounces", NEVER write "बounces").
- Do NOT add or remove facts. Translate/paraphrase ONLY the given English text.
- Do NOT include any topics or facts from the example (such as water or growth) in your output.

[Example Input]
Plants need water for growth.
[Example Output]
पौधों को विकास (Growth) के लिए पानी (Water) की आवश्यकता होती है।

{retry_block}
[Target Input]
{english_text.strip()}
[Target Output]"""


def build_quiz_question_localize_prompt(
    question: dict[str, str],
    *,
    class_level: int | None = None,
    strict_retry: bool = False,
) -> str:
    """Build prompt to translate one MCQ into Hinenglish JSON."""
    retry_block = f"\n{_STRICT_RETRY_SUFFIX}\n" if strict_retry else ""
    return f"""{HINDI_LOCALIZE_MARKER}

Convert this English MCQ into Hinenglish. Return ONLY valid JSON with keys:
question, option_a, option_b, option_c, option_d, correct_answer

Rules:
- Translate question and options into Devanagari Hindi (Hinenglish).
- Keep correct_answer exactly as "{question.get('correct_answer', 'A')}" (single letter A/B/C/D).
- Keep proper nouns, formulas, and numbers unchanged.
- Do NOT mix English and Hindi letters in a single word (e.g. write "बाउंस" or "bounces", NEVER write "बounces").
- Do NOT add or remove options.
{_class_hint(class_level)}

[Example English MCQ JSON]
{{
  "question": "What is the process of food making in plants called?",
  "option_a": "Photosynthesis",
  "option_b": "Respiration",
  "option_c": "Transpiration",
  "option_d": "Translocation",
  "correct_answer": "A"
}}
[Example JSON output]
{{
  "question": "पौधों में भोजन बनाने की प्रक्रिया को क्या कहा जाता है?",
  "option_a": "प्रकाश संश्लेषण (Photosynthesis)",
  "option_b": "श्वसन (Respiration)",
  "option_c": "वाष्पोत्सर्जन (Transpiration)",
  "option_d": "स्थानांतरण (Translocation)",
  "correct_answer": "A"
}}

{retry_block}
[Target English MCQ JSON]
{{
  "question": {question.get('question', '')!r},
  "option_a": {question.get('option_a', '')!r},
  "option_b": {question.get('option_b', '')!r},
  "option_c": {question.get('option_c', '')!r},
  "option_d": {question.get('option_d', '')!r},
  "correct_answer": {question.get('correct_answer', 'A')!r}
}}

[Target JSON output]"""
