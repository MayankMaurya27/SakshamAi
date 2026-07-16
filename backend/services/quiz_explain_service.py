"""Rich quiz answer explanation service for Saksham AI.

Generates detailed, educationally valuable explanations after a student
answers a quiz question. Optimized for Llama 3.2 1B token limits via text markers.
"""

import logging
import re
from typing import Any

from ai.llm import get_llm
from ai.prompt_builder import EXPLAIN_TEXT_PROMPT
from services.quiz_explain_cache import load_cached_explanation, save_cached_explanation

logger = logging.getLogger(__name__)


def _compute_deterministic_metadata(
    question: str,
    topic: str | None,
    subject: str | None,
    class_level: int | None,
    is_correct: bool,
) -> dict[str, Any]:
    """Compute explanation metadata deterministically without LLM."""
    q_len = len(question)
    if q_len < 60:
        diff = "Easy"
    elif q_len > 120:
        diff = "Hard"
    else:
        diff = "Medium"

    base_topic = topic or "General Knowledge"
    sub_str = f" in {subject}" if subject else ""
    
    return {
        "difficulty": diff,
        "topic": base_topic,
        "common_misconception": "Students often confuse similar-sounding concepts.",
        "related_concept": f"Review the related section{sub_str}.",
        "follow_up_question": "Can you explain this concept in your own words?",
        "study_suggestion": "Great job! Keep practicing." if is_correct else f"Re-read the {base_topic} section to clarify this.",
    }


def _parse_text_explanation(text: str, options: dict[str, str], correct_answer: str) -> dict[str, Any]:
    """Parse the text-marker output from the LLM."""
    parsed = {}
    correct_text = options.get(correct_answer, correct_answer)

    text_upper = text.upper()

    def extract_section(start_keywords, end_keywords):
        start_idx = -1
        for kw in start_keywords:
            idx = text_upper.find(kw)
            if idx != -1:
                start_idx = idx + len(kw)
                break
        
        if start_idx == -1:
            return ""
            
        end_idx = len(text)
        for kw in end_keywords:
            idx = text_upper.find(kw, start_idx)
            if idx != -1 and idx < end_idx:
                end_idx = idx
                
        return text[start_idx:end_idx].strip(": \n-[]")

    # 1. Why Correct
    why_corr = extract_section(
        ["[WHY_CORRECT]", "WHY_CORRECT", "WHY THE CORRECT ANSWER IS RIGHT", "CORRECT ANSWER:"], 
        ["[WRONG_", "WRONG_", "EXAMPLE", "[EXAMPLE]", "TRICK", "[TRICK]"]
    )
    if not why_corr or len(why_corr) < 10:
        why_corr = f"The correct answer is {correct_answer} because {correct_text} is the right choice."
    
    if why_corr.upper().startswith(f"{correct_answer} (") or why_corr.upper().startswith(f"{correct_answer} -"):
        idx = why_corr.find("\n")
        if idx != -1:
            why_corr = why_corr[idx:].strip()

    parsed["why_correct"] = why_corr
    parsed["easy_explanation"] = why_corr

    # 2. Why Wrong
    why_wrong = {}
    for letter in ("A", "B", "C", "D"):
        if letter != correct_answer:
            ans = extract_section(
                [f"[WRONG_{letter}]", f"WRONG_{letter}"], 
                ["[WRONG_", "WRONG_", "EXAMPLE", "[EXAMPLE]", "TRICK", "[TRICK]"]
            )
            if not ans or len(ans) < 10:
                ans = f"This option is incorrect because the correct answer is {correct_text}."
            why_wrong[letter] = ans
    parsed["why_wrong"] = why_wrong

    # 3. Example & Trick
    parsed["real_world_example"] = extract_section(["[EXAMPLE]", "EXAMPLE"], ["[TRICK]", "TRICK"]) or "Think about how this applies in everyday life."
    parsed["memory_trick"] = extract_section(["[TRICK]", "TRICK"], []) or f"Remember: the answer is {correct_answer} for this concept."

    return parsed


def generate_quiz_explanation(
    question: str,
    options: dict[str, str],
    correct_answer: str,
    student_answer: str,
    topic: str | None = None,
    subject: str | None = None,
    class_level: int | None = None,
) -> dict[str, Any]:
    """Generate a rich explanation for a quiz answer using text markers."""
    correct_answer = correct_answer.upper().strip()
    student_answer = student_answer.upper().strip()
    is_correct = student_answer == correct_answer

    # 1. Check Cache
    cached = load_cached_explanation(question)
    if cached:
        cached["is_correct"] = is_correct  # Dynamic based on current student's answer
        return cached

    # 2. Generate via LLM (No JSON)
    correct_text = options.get(correct_answer, "")
    prompt = EXPLAIN_TEXT_PROMPT.format(
        question=question,
        option_a=options.get("A", ""),
        option_b=options.get("B", ""),
        option_c=options.get("C", ""),
        option_d=options.get("D", ""),
        correct_answer=correct_answer,
        correct_text=correct_text,
    )

    try:
        llm = get_llm()
        # format_json=False is critical here for llama3.2:1b marker prompt
        response = llm.generate(prompt, num_predict=600, format_json=False)
        print("RAW LLM OUTPUT:")
        print(response)
        parsed = _parse_text_explanation(response, options, correct_answer)
        logger.info("Generated quiz explanation via LLM text markers")
    except Exception as exc:
        logger.error("Quiz explanation LLM error: %s", exc)
        # Extreme fallback if LLM completely crashes
        parsed = _parse_text_explanation("", options, correct_answer)

    # 3. Add Deterministic Metadata
    metadata = _compute_deterministic_metadata(question, topic, subject, class_level, is_correct)
    parsed.update(metadata)
    
    # Base state
    parsed["is_correct"] = is_correct

    # 4. Save Cache (save without is_correct since that's student-specific)
    cache_payload = parsed.copy()
    cache_payload.pop("is_correct", None)
    save_cached_explanation(question, cache_payload)

    return parsed


def generate_batch_explanations(
    questions: list[dict[str, Any]],
    student_answers: dict[int, str],
    topic: str | None = None,
    subject: str | None = None,
    class_level: int | None = None,
) -> list[dict[str, Any]]:
    """Generate explanations for multiple quiz questions."""
    explanations = []
    for idx, q in enumerate(questions):
        student_ans = student_answers.get(idx, "")
        if not student_ans:
            explanations.append(None)
            continue

        options = q.get("options", {})
        if not options:
            options = {
                "A": q.get("option_a", ""),
                "B": q.get("option_b", ""),
                "C": q.get("option_c", ""),
                "D": q.get("option_d", ""),
            }

        explanation = generate_quiz_explanation(
            question=q.get("question", ""),
            options=options,
            correct_answer=q.get("correct_answer", "A"),
            student_answer=student_ans,
            topic=topic,
            subject=subject,
            class_level=class_level,
        )
        explanations.append(explanation)

    return explanations
