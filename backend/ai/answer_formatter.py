"""Post-process LLM answers for student-facing clarity and safety."""

import re

_START_PATTERNS = [
    re.compile(r"^You are right to ask.+?\.\s+", re.I | re.S),
    re.compile(r"^The student asked.+?\.\s+", re.I | re.S),
    re.compile(r"^According to the context,?\s*", re.I),
    re.compile(r"^I(?:'d| would) be happy to help.+?\.\s+", re.I | re.S),
    re.compile(r"^Welcome to .+?(?:\.\s+|\!\s*)", re.I | re.S),
    re.compile(r"^Here(?:'s| is) a (?:clear )?explanation.+?\.\s+", re.I | re.S),
]

_END_PATTERNS = [
    re.compile(r"\s*Let(?:'s| us) move on to another topic\.?\s*$", re.I),
    re.compile(r"\s*Do you have any (?:further )?questions[^.]*\??\s*$", re.I),
    re.compile(r"\s*Let me know if you (?:have|need)[^.]*[.?.]\s*$", re.I),
    re.compile(r"\s*I hope this helps[^.]*[.?.]\s*$", re.I),
    re.compile(
        r"\s*Please let me know if you have any further questions[^.]*[.?.]\s*$",
        re.I,
    ),
    re.compile(r"\s*Would you like me to .+?\??\s*$", re.I | re.S),
]

_MERGED_WORD_FIXES = [
    (re.compile(r"\bthesubstance\b", re.I), "the substance"),
    (re.compile(r"\bforma solution\b", re.I), "form a solution"),
    (re.compile(r"\bsolute\)to\b", re.I), "solute) to"),
    (re.compile(r"\banobject\b", re.I), "an object"),
    (re.compile(r"\bWhen anobject\b", re.I), "When an object"),
    (re.compile(r"\bitcan\b", re.I), "it can"),
    (re.compile(r"\bmirroris\b", re.I), "mirror is"),
    (re.compile(r"\barecurved\b", re.I), "are curved"),
    (re.compile(r"\blightrays\b", re.I), "light rays"),
    (re.compile(r"\borspreads\b", re.I), "or spreads"),
    (re.compile(r"\bAconvex\b", re.I), "A convex"),
    (re.compile(r"\bImagineyou\b", re.I), "Imagine you"),
    (re.compile(r"\bitwill\b", re.I), "it will"),
    (re.compile(r"\busedto\b", re.I), "used to"),
]


def format_student_answer(answer: str) -> str:
    """Strip chatbot filler and fix common formatting issues in LLM output."""
    if not answer:
        return answer

    text = answer.strip()

    for pattern in _START_PATTERNS:
        text = pattern.sub("", text, count=1).lstrip()

    for pattern in _END_PATTERNS:
        text = pattern.sub("", text).rstrip()

    for pattern, replacement in _MERGED_WORD_FIXES:
        text = pattern.sub(replacement, text)

    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
