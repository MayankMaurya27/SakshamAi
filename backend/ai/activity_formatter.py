"""Format textbook activity answers directly from retrieved passage text."""

import re
from enum import Enum

from ai.context_cleaner import clean_context_text

_MAX_PROCEDURE_STEPS = 5


class ActivityIntent(str, Enum):
    """Which part of an activity the student is asking about."""

    FULL = "full"
    AIM = "aim"
    PROCEDURE = "procedure"
    OBSERVATION = "observation"
    CONCLUSION = "conclusion"
    FOCUS = "focus"


def detect_activity_intent(question: str) -> ActivityIntent:
    """Detect whether the student wants the full activity or a specific part."""
    q = question.lower().strip()

    if re.search(r"\b(?:explain|describe|tell me about)\s+(?:the\s+)?activity\b", q):
        return ActivityIntent.FULL
    if re.search(r"\bwhat is the activity\b|\bwhat is activity\b", q):
        return ActivityIntent.FULL

    if re.search(
        r"\bconclusion\b|\bconclude\b|\bwhat can we (?:infer|conclude)\b|"
        r"\bwhat do we infer\b|\bwhat can you infer\b",
        q,
    ):
        return ActivityIntent.CONCLUSION

    if re.search(
        r"\bobservation\b|\bwhat do you observe\b|\bwhat do we observe\b|\bwhat happens when\b",
        q,
    ):
        return ActivityIntent.OBSERVATION

    if re.search(r"\bprocedure\b|\bsteps to\b|\bhow (?:to|do we) (?:do|perform)\b", q):
        return ActivityIntent.PROCEDURE

    if re.search(r"\baim\b|\bpurpose of the activity\b", q):
        return ActivityIntent.AIM

    return ActivityIntent.FOCUS

_DIAGRAM_LABEL_LINE = re.compile(
    r"^(?:Water|More water|Balloon bulges out(?: more)?|Bottle|Holes|Stand|"
    r"Broad pipe|Narrow pipe|Balloons|Sunrays|Illuminated|Non-\s*illuminated)$",
    re.I,
)
_PAGE_NOISE = re.compile(r"\.{6,}", re.I)
_DIAGRAM_LETTERS = re.compile(r"(?:\b[A-H]\b\s*){4,}")


def _shorten_sentences(text: str, max_sentences: int) -> str:
    """Keep only the first few complete sentences from a block of text."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    return " ".join(parts[:max_sentences]).strip()


def _normalize_activity_passage(text: str, activity_ref: str) -> str:
    """Drop duplicated activity headers caused by overlapping PDF chunks."""
    lower = text.lower()
    ref_lower = activity_ref.lower()
    first = lower.find(ref_lower)
    if first > 0:
        text = text[first:]
        lower = text.lower()

    second = lower.find(ref_lower, len(ref_lower) + 20)
    if second > 0 and second < 600:
        text = text[second:]
    return text


def _strip_layout_noise(text: str) -> str:
    """Remove figure caption lines and PDF layout labels."""
    lines: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if re.match(r"^Fig\.\s*\d+", stripped, re.I):
            continue
        if _DIAGRAM_LABEL_LINE.match(stripped):
            continue
        if re.match(r"^Chapter \d+", stripped, re.I) and "observe" not in stripped.lower():
            continue
        if re.match(r"^Reprint", stripped, re.I):
            continue
        if re.search(r"Curiosity.*Grade \d+", stripped, re.I) and len(stripped) < 100:
            continue
        lines.append(line)

    text = "\n".join(lines)
    text = _PAGE_NOISE.sub("", text)
    text = _DIAGRAM_LETTERS.sub(" ", text)
    text = re.sub(r"Why does the illuminated portion[^?]+\?", " ", text, flags=re.I)
    text = re.sub(
        r"(What do you observe\?)\s*(?:Water|More water|Balloon bulges out(?: more)?\s*)+",
        r"\1 ",
        text,
        flags=re.I,
    )
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _dedupe_procedure_steps(steps: list[str]) -> list[str]:
    """Drop truncated or duplicate procedure steps from overlapping chunks."""
    kept: list[str] = []
    for step in steps:
        step = step.strip()
        replaced = False
        for index, existing in enumerate(kept):
            existing_lower = existing.lower()
            step_lower = step.lower()
            if step_lower.startswith(existing_lower) and len(step) > len(existing) + 5:
                kept[index] = step
                replaced = True
                break
            if existing_lower.startswith(step_lower) and len(existing) > len(step) + 5:
                replaced = True
                break
        if not replaced:
            kept.append(step)
    return kept


def _clean_step_text(step: str) -> str:
    """Remove figure references and tighten spacing in a procedure step."""
    step = re.sub(r"\(Fig\.\s*[^)]+\)", "", step)
    step = re.sub(r"\s+as shown in Fig\.\s*[\d.]+[a-z]?", "", step, flags=re.I)
    step = re.sub(r"\s+", " ", step).strip()
    step = re.sub(r"\s+\.", ".", step)
    step = re.sub(r"\.{2,}", ".", step)
    return step


def _action_before_questions(step: str) -> str:
    """Keep the actionable part of a step and drop trailing questions."""
    step = _clean_step_text(step)
    step = re.sub(r"\s+Does the .+\?$", ".", step, flags=re.I)
    step = re.sub(r"\s+Do (?:both|you).+\?$", ".", step, flags=re.I)
    step = re.sub(r"\s+Is the line.+\?$", ".", step, flags=re.I)
    if "?" not in step:
        return step.strip()
    before = step.split("?")[0].strip()
    if len(before) >= 30:
        return before + "."
    return ""


def _split_procedure_and_prompts(steps: list[str]) -> tuple[list[str], list[str]]:
    """Separate hands-on steps from observation prompts."""
    procedure: list[str] = []
    prompts: list[str] = []

    for step in steps:
        lower = step.lower()
        if re.match(r"^(was your observation|do both|does the|is the line)", lower):
            prompts.append(step)
            continue
        if step.count("?") >= 2:
            prompts.append(step)
            action = _action_before_questions(step)
            if action:
                procedure.append(action)
            continue

        action = _action_before_questions(step)
        if action:
            procedure.append(action)
        elif "?" in step:
            prompts.append(step)

    return _dedupe_procedure_steps(procedure), prompts


def _extract_bullet_steps(text: str) -> list[str]:
    """Extract procedure bullets until an observation section begins."""
    lower = text.lower()
    end = len(text)
    for marker in (
        "what do you observe?",
        "was your observation",
        "you observe water",
        "you must have observed",
        "what can you infer",
        "when the ball is held",
    ):
        idx = lower.find(marker)
        if 0 <= idx < end:
            end = idx

    steps: list[str] = []
    for line in text[:end].split("\n"):
        line = line.strip()
        if line.startswith("- "):
            step = line[2:].strip()
            if len(step) >= 10:
                steps.append(step)
    return steps


def _extract_observation(text: str) -> str:
    """Extract what students observe during the activity."""
    patterns = [
        r"You must have observed that .+?(?=Pour some more water|Fig\.\s*\d|What can you infer|What do we infer|Thus,|So, we can say|You must have seen|Let us now try|Ever heard of|Activity\s+\d)",
        r"You observe .+?(?=What can you infer|What do we infer|Therefore,|You must have seen|Let us now try|Ever heard of|Activity\s+\d)",
        r"We observe that .+?(?=What do we infer|What can you infer|z Now bring|Fig\.\s*\d|Activity\s+\d)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return match.group(0).strip()
    return ""


def _extract_activity_explanation(text: str) -> str:
    """Extract the textbook explanation that follows hands-on steps."""
    patterns = [
        r"When the ball is held opposite.+?on other days\.",
        r"The shape of the illuminated portion of the ball.+?with respect to the lamp\.",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return match.group(0).strip()
    return ""


def _extract_follow_up(text: str) -> str:
    """Extract optional follow-up steps inside an activity."""
    match = re.search(
        r"Pour some more water.+?"
        r"(?=Thus,|So, we can say|What can you infer from this observation|You must have seen|Let us now try|Ever heard of|Activity\s+\d)",
        text,
        re.I | re.S,
    )
    return match.group(0).strip() if match else ""


def _extract_conclusion(text: str) -> str:
    """Extract inference and conclusion statements from the activity."""
    blocks: list[str] = []

    _STOP = (
        r"Suppose you are living|Let us now try|Ever heard of|Activity\s+\d|"
        r"You must have seen water spurting|Gravitational force|$"
    )

    infer = re.search(
        r"What can you infer[^?]*\?\s*(.+?)(?=Pour some more|You must have seen water spurting|"
        + _STOP
        + r")",
        text,
        re.I | re.S,
    )
    if infer:
        blocks.append(infer.group(1).strip())

    infer_we = re.search(
        r"What do we infer from these observations\?\s*(.+?)(?=Gravitational force|Activity\s+\d|$)",
        text,
        re.I | re.S,
    )
    if infer_we:
        blocks.append(infer_we.group(1).strip())

    found = re.search(
        r"We found that .+?non-contact force\.",
        text,
        re.I | re.S,
    )
    if found:
        blocks.append(found.group(0).strip())

    thus = re.search(
        rf"(Thus,.+?)(?={_STOP})",
        text,
        re.I | re.S,
    )
    if thus:
        blocks.append(thus.group(1).strip())

    so = re.search(
        rf"(So, we can say.+?)(?=This is the reason why overhead|{_STOP})",
        text,
        re.I | re.S,
    )
    if so and so.group(1) not in blocks:
        blocks.append(so.group(1).strip())

    fountain = re.search(
        r"You must have seen water spurting.+?(?:walls of the pipes\?|pipes\.)",
        text,
        re.I | re.S,
    )
    if fountain:
        blocks.append(fountain.group(0).strip())

    if not blocks:
        return ""

    unique_blocks: list[str] = []
    for block in blocks:
        if block not in unique_blocks:
            unique_blocks.append(block)
    conclusion = " ".join(unique_blocks)
    conclusion = re.sub(r"\s*\.{6,}.*$", "", conclusion, flags=re.S).strip()
    return conclusion


def _extract_aim(text: str, activity_ref: str) -> str:
    """Extract a short aim line for the activity."""
    intro = re.search(
        rf"activity to understand (.+?)\.\s*{re.escape(activity_ref)}",
        text,
        re.I | re.S,
    )
    if intro:
        return intro.group(1).strip().capitalize() + "."

    aim_match = re.search(
        rf"{re.escape(activity_ref)}:\s*(.+?)(?:\n|$)",
        text,
        re.I,
    )
    if aim_match:
        return aim_match.group(1).strip()
    return "Activity from the textbook."


def _summarize_observation(
    prompts: list[str],
    classic_observation: str,
    explanation: str,
) -> str:
    """Build a short observation line."""
    for prompt in prompts:
        if "shape of the illuminated" in prompt.lower():
            after = prompt.split("?")[-1].strip()
            if after:
                return _shorten_sentences(after, 1)

    if classic_observation:
        return _shorten_sentences(classic_observation, 1)

    if explanation:
        return _shorten_sentences(explanation, 1)

    if prompts:
        return _shorten_sentences(prompts[0], 1)
    return ""


def _truncate_step(step: str, max_len: int = 150) -> str:
    """Keep procedure steps readable without copying entire paragraphs."""
    if len(step) <= max_len:
        return step
    return _shorten_sentences(step, 1)


def _summarize_conclusion(explanation: str, conclusion: str) -> str:
    """Build a short conclusion line."""
    if conclusion:
        cleaned = re.sub(r"Fig\.\s*\d+[^.]*\.", " ", conclusion)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        for marker in (
            "We found that",
            "We can infer that",
            "So, we can say",
            "Thus,",
            "Therefore,",
            "In fact",
        ):
            idx = cleaned.find(marker)
            if idx >= 0:
                text = cleaned[idx:]
                text = re.sub(r"\(Fig\.[^)]*$", "", text).strip()
                return _shorten_sentences(text, 3)
        text = re.sub(r"\(Fig\.[^)]*$", "", cleaned).strip()
        return _shorten_sentences(text, 2)
    if explanation:
        sentences = re.split(r"(?<=[.!?])\s+", explanation.strip())
        if len(sentences) >= 3:
            text = " ".join(sentences[1:4])
            text = re.sub(r"\(Fig\.[^)]*$", "", text).strip()
            return text
        return _shorten_sentences(explanation, 2)
    return ""


def try_format_activity_answer(
    passage: str,
    activity_ref: str,
    intent: ActivityIntent = ActivityIntent.FULL,
) -> str | None:
    """
    Build a concise student answer from the activity passage without LLM paraphrasing.

    Returns None if the passage does not contain a usable activity block.
    """
    raw_text = _normalize_activity_passage(clean_context_text(passage), activity_ref)
    if activity_ref.lower() not in raw_text.lower():
        return None

    classic_observation = _extract_observation(raw_text)
    follow_up = _extract_follow_up(raw_text)
    conclusion = _extract_conclusion(raw_text)
    explanation = _extract_activity_explanation(raw_text)

    text = _strip_layout_noise(raw_text)
    all_steps = _extract_bullet_steps(text)
    if not all_steps and intent not in (ActivityIntent.CONCLUSION, ActivityIntent.OBSERVATION):
        return None

    procedure, prompts = _split_procedure_and_prompts(all_steps)
    aim = _extract_aim(text, activity_ref)
    observation = _summarize_observation(prompts, classic_observation, explanation)
    summary = _summarize_conclusion(explanation, conclusion)

    if intent == ActivityIntent.CONCLUSION:
        if summary:
            return summary
        found = re.search(
            r"We found that .+?non-contact force\.",
            raw_text,
            re.I | re.S,
        )
        if found:
            return _summarize_conclusion("", found.group(0).strip())
        if conclusion:
            return _shorten_sentences(conclusion, 4)
        return None

    if intent == ActivityIntent.OBSERVATION:
        if observation:
            return observation
        if classic_observation:
            return _shorten_sentences(classic_observation, 2)
        return None

    if intent == ActivityIntent.AIM:
        return aim

    if intent == ActivityIntent.PROCEDURE:
        if not procedure:
            return None
        lines = [f"{index}. {step}" for index, step in enumerate(procedure[:_MAX_PROCEDURE_STEPS], 1)]
        return "\n".join(lines)

    if not procedure:
        return None

    procedure = [_truncate_step(step) for step in procedure[:_MAX_PROCEDURE_STEPS]]

    parts = [f"Aim\n{aim}", "Procedure"]
    parts.extend(f"{index}. {step}" for index, step in enumerate(procedure, 1))

    if observation:
        parts.append(f"Observation\n{observation}")

    if follow_up:
        parts.append(f"Follow-up\n{_shorten_sentences(follow_up, 2)}")

    if summary:
        parts.append(f"Conclusion\n{summary}")

    return "\n\n".join(parts)
