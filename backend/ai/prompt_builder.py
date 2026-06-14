"""Centralized prompt template construction and routing."""

from config.constants import LearningMode, AnswerProfile

STRICT_SYSTEM_PROMPT = """You are Saksham AI, an offline educational assistant for Indian school students.

STRICT RULES:
- Use ONLY the provided context. Never add outside knowledge.
- Explain clearly in your own words. Do not copy long paragraphs from the context.
- Answer ONLY what the student asked. Keep answers focused unless more detail is requested.
- Start directly with the answer. No greetings or chatbot phrases.
- Never say: "Welcome", "I'd be happy to help", "The student asked", "According to the context", "Let me know if", "Let's move on", "Do you have any questions".
- Do not paste exercise questions, figure captions, page headers, or textbook introductions.
- Do not invent activities, figures, examples, or scientific claims.
- If the answer is not in the context, reply exactly: "This was not found in the chapter content."

Write in clear, simple English for the student's class level."""

GUIDED_SYSTEM_PROMPT = """You are Saksham AI, an offline educational assistant for Indian school students.

RULES:
- Use ONLY facts supported by the provided chapter context. Do not invent examples, numbers, people, or claims.
- You may reorganise and explain the context clearly like a teacher. Prefer explanation over copying long passages.
- Quote the textbook only for key terms or short phrases when helpful.
- Answer the exact question asked completely, using only relevant points from the context.
- Ignore unrelated parts of the context that do not answer the question.
- Start directly with the answer. No greetings or chatbot phrases.
- Never say: "Welcome", "I'd be happy to help", "The student asked", "According to the context", "Let me know if", "Let's move on", "Do you have any questions".
- Do not paste exercise questions, figure captions, page headers, or textbook introductions.
- Do not invent activities, figures, or examples not supported by the context.
- If the context does not contain enough information to answer, reply exactly: "This was not found in the chapter content."

Write in clear, simple English for the student's class level."""

# Backward-compatible alias used in tests and older imports.
GLOBAL_SYSTEM_PROMPT = GUIDED_SYSTEM_PROMPT

FALLBACK_RESPONSE = (
    "The required information was not found in the available educational content. "
    "Please upload a relevant document or choose another topic."
)

STRICT_LEARN_INSTRUCTIONS = """Instructions:
Answer using only the provided context.
Explain clearly in your own words. Do not copy long passages from the context.
Keep the answer focused on what the student asked.
Do not use Aim, Procedure, Observation, or Conclusion headings unless the question asks about a specific activity or figure.
Do not add extra topics or revision sections."""

GUIDED_LEARN_INSTRUCTIONS = """Instructions:
Answer using only facts from the context above.
Explain clearly in your own words. Do not copy long passages.
Give a complete answer to the question. Ignore unrelated context.
Do not use Aim, Procedure, Observation, or Conclusion headings unless the question asks about a specific activity or figure.
Do not add unrelated revision sections."""

BROAD_QUESTION_ADDENDUM = """
This is a broad chapter question. Structure the answer clearly. Include the main points the question needs, such as:
- background or causes (if relevant)
- key events, ideas, or processes
- outcomes or significance
- important limits or contradictions mentioned in the context (for example, who was included or excluded)
Stay accurate and aligned with the chapter."""

QUIZ_TEXT_OUTPUT_FORMAT = """Output format (plain text only — do NOT use JSON):
Repeat this block for each question:

Question 1: <question text>
A. <option A>
B. <option B>
C. <option C>
D. <option D>
Answer: A

Question 2: <next question>
A. ...
B. ...
C. ...
D. ...
Answer: B

Output rules:
- Write plain text only. No JSON, no code fences, no prose before or after the questions.
- Number questions starting at 1.
- Put each option on its own line with labels A., B., C., D.
- Every question MUST end with a line: Answer: X (where X is A, B, C, or D).
- Vary the correct answer letter across questions."""

TEMPLATES: dict[LearningMode, str] = {
    LearningMode.LEARN: """Context:
{retrieved_context}

{chapter_section}Question:
{question}

{learn_instructions}{broad_addendum}""",
    LearningMode.SIMPLIFY: """Context:
{retrieved_context}

Question:
{question}

Instructions:
Explain as if teaching a Class 6 student.
Use simple words.
Use short sentences.
Use everyday examples.
Stay aligned with the context. You may add brief school-level clarification if needed.""",
    LearningMode.HINDI: """Context:
{retrieved_context}

Question:
{question}

Instructions:
Explain in Hindi.
Keep educational terms accurate.
Use simple Hindi.
If an English scientific term is commonly used, include it in brackets.
Stay aligned with the context.""",
    LearningMode.QUIZ: """Context:
{retrieved_context}

{chapter_section}Instructions:
Generate exactly {question_count} multiple-choice questions from the context above.

Question rules:
- Use ONLY facts from the provided context.
- Do not copy exercise questions verbatim from the context.
- Cover different parts of the context when possible.
- Avoid duplicate or near-duplicate questions.
- For math chapters, write numeric options clearly (for example: 0.2, 1/10, 2.5).

""" + QUIZ_TEXT_OUTPUT_FORMAT,
    LearningMode.SUMMARY: """Context:
{retrieved_context}

Instructions:
Generate concise study notes.
Return:
- Key Concepts
- Important Points
- Revision Notes

Maximum 10 bullet points.""",
    LearningMode.KEY_CONCEPTS: """Document:
{document_text}

Instructions:
Extract the most important educational concepts.
Return:
- Concept Name
- One-line Description

Maximum 10 concepts.
Return valid JSON with a "concepts" array.""",
    LearningMode.AUTO_ANALYSIS: """Document:
{document_text}

Instructions:
Analyze the document.
Generate:
1. Short Summary
2. Key Concepts (name and one-line description)
3. 5 Practice Questions (with four options and correct answer)

Return valid JSON with keys: summary, key_concepts, questions.""",
    LearningMode.BEGINNER: """Context:
{retrieved_context}

Question:
{question}

Instructions:
Explain using very simple language.
Assume no prior knowledge.
Use analogies and real-life examples.
Stay aligned with the context.""",
    LearningMode.DYSLEXIA: """Context:
{retrieved_context}

Question:
{question}

Instructions:
Use:
- Short sentences
- Small paragraphs
- Simple words

Avoid:
- Long paragraphs
- Complex terminology

Structure answer with bullets.""",
    LearningMode.VISUAL: """Context:
{retrieved_context}

Question:
{question}

Instructions:
Provide a complete answer optimized for audio narration.
Use short sections.
Avoid tables.
Avoid complex formatting.""",
    LearningMode.LEARN_FROM_SAKSHAM: """Context:
{retrieved_context}

Chapter:
{topic}

Question:
{question}

{learn_instructions}{broad_addendum}""",
}

MATH_QUIZ_TEMPLATE = """Context:
{retrieved_context}

Validated chapter calculations (reference only):
{math_facts_reference}

{chapter_section}Instructions:
Generate exactly {question_count} NEW multiple-choice math questions for Class {grade}.

Question style:
- Test math skills: calculations, decimal operations, place value, definitions, and procedures.
- Each question must be self-contained and at most 120 characters.
- Do NOT mention story characters (Jonali, Pallabi, Arshad, Ajay).
- Do NOT copy textbook headings, "Example N:", or exercise instructions.
- Do NOT paste long story setups or worksheet text.

Options:
- Four distinct numeric or short math answers.
- Only one correct option.
- Vary correct_answer across A, B, C, and D.

""" + QUIZ_TEXT_OUTPUT_FORMAT

SCIENCE_QUIZ_TEMPLATE = """Context:
{retrieved_context}

{chapter_section}Instructions:
Generate exactly {question_count} multiple-choice science questions for Class {grade}.

Question style:
- Ask about facts, definitions, processes, and concepts from the chapter.
- Each question must be a clear factual MCQ with one correct answer.
- Keep each question under 140 characters.
- Do NOT copy rhetorical questions, activity instructions, or textbook introductions.
- Do NOT paste long sentences from the context as the question.
- Use simple English suitable for Class {grade}.

Options:
- Four distinct answer choices.
- Only one correct option.
- Vary correct_answer across A, B, C, and D.

""" + QUIZ_TEXT_OUTPUT_FORMAT

_STRICT_MODES = frozenset(
    {
        LearningMode.QUIZ,
        LearningMode.SUMMARY,
        LearningMode.KEY_CONCEPTS,
        LearningMode.AUTO_ANALYSIS,
    }
)


def _default_profile_for_mode(mode: LearningMode) -> AnswerProfile:
    if mode in _STRICT_MODES:
        return AnswerProfile.STRICT
    return AnswerProfile.GUIDED


def _system_prompt(profile: AnswerProfile, grade: int) -> str:
    if profile == AnswerProfile.STRICT:
        return STRICT_SYSTEM_PROMPT
    return GUIDED_SYSTEM_PROMPT.format(grade=grade)


def _learn_instructions(profile: AnswerProfile, grade: int) -> str:
    if profile == AnswerProfile.STRICT:
        return STRICT_LEARN_INSTRUCTIONS
    return GUIDED_LEARN_INSTRUCTIONS


def build_prompt(
    mode: LearningMode,
    retrieved_context: str = "",
    question: str = "",
    document_text: str = "",
    topic: str = "",
    grade: int = 8,
    answer_profile: AnswerProfile | None = None,
    broad_question: bool = False,
    question_count: int = 5,
) -> str:
    """Build a complete prompt for the given learning mode."""
    template = TEMPLATES.get(mode)
    if template is None:
        raise ValueError(f"Unknown learning mode: {mode}")

    profile = answer_profile or _default_profile_for_mode(mode)
    chapter_section = f"Chapter:\n{topic}\n\n" if topic else ""
    learn_instructions = _learn_instructions(profile, grade)
    broad_addendum = BROAD_QUESTION_ADDENDUM if broad_question and profile == AnswerProfile.GUIDED else ""

    format_kwargs = {
        "retrieved_context": retrieved_context,
        "question": question,
        "document_text": document_text,
        "topic": topic,
        "grade": grade,
        "chapter_section": chapter_section,
        "learn_instructions": learn_instructions,
        "broad_addendum": broad_addendum,
    }
    if mode == LearningMode.QUIZ:
        format_kwargs["question_count"] = question_count
    body = template.format(**format_kwargs)
    return f"{_system_prompt(profile, grade)}\n\n{body}"


def build_quiz_prompt(
    retrieved_context: str,
    question_count: int,
    topic: str = "",
    grade: int = 8,
    subject: str | None = None,
    math_facts_reference: str = "",
    chapter_kind: str | None = None,
) -> str:
    """Build a strict quiz-generation prompt."""
    from services.quiz_math import is_math_subject
    from services.quiz_science import is_science_subject

    if is_math_subject(subject):
        chapter_section = f"Chapter:\n{topic}\n\n" if topic else ""
        focus_line = ""
        if chapter_kind == "expressions":
            focus_line = (
                "Focus on arithmetic expressions, evaluating expressions, brackets, "
                "and the meaning of '='. Do not ask geometry questions.\n"
            )
        elif chapter_kind == "geometry":
            focus_line = "Focus on triangles, side lengths, and geometric definitions from this chapter.\n"
        elif chapter_kind == "decimals":
            focus_line = "Focus on decimal operations and place value from this chapter.\n"
        body = MATH_QUIZ_TEMPLATE.format(
            retrieved_context=retrieved_context,
            math_facts_reference=math_facts_reference or "- None extracted",
            chapter_section=chapter_section,
            question_count=question_count,
            grade=grade,
        )
        if focus_line:
            body = focus_line + body
        return f"{STRICT_SYSTEM_PROMPT}\n\n{body}"

    if is_science_subject(subject):
        chapter_section = f"Chapter:\n{topic}\n\n" if topic else ""
        body = SCIENCE_QUIZ_TEMPLATE.format(
            retrieved_context=retrieved_context,
            chapter_section=chapter_section,
            question_count=question_count,
            grade=grade,
        )
        return f"{STRICT_SYSTEM_PROMPT}\n\n{body}"

    return build_prompt(
        LearningMode.QUIZ,
        retrieved_context=retrieved_context,
        topic=topic,
        grade=grade,
        question_count=question_count,
    )


SUMMARY_PROSE_INSTRUCTIONS = """Output format (plain text only — do NOT use JSON, headings, or bullet lists):
Write at least 2-3 short paragraphs for a Class {grade} student.
Add more paragraphs only if the context covers many distinct ideas.
Separate each paragraph with one blank line."""


def build_summary_prompt(
    retrieved_context: str,
    topic: str = "",
    grade: int = 8,
    window_hint: str = "",
    mode: str = "full",
) -> str:
    """Build a plain-text chapter/document summary prompt for the local LLM."""
    chapter_section = f"Chapter:\n{topic}\n\n" if topic else ""
    hint = f"{window_hint}\n\n" if window_hint else ""

    if mode == "partial":
        task = (
            "Write revision notes for this section of the chapter using ONLY the context above. "
            "Use 2-3 short paragraphs. This is one part of a longer chapter."
        )
    elif mode == "synthesis":
        task = (
            "Combine the partial revision notes below into one clear chapter summary. "
            "Use at least 3 paragraphs and add more only if needed. "
            "Remove repetition and keep the flow easy to read."
        )
    else:
        task = (
            "Write revision notes for the full chapter using ONLY the context above. "
            "Use at least 2-3 paragraphs and add more only if the chapter covers many ideas."
        )

    body = f"""Context:
{retrieved_context}

{chapter_section}{hint}Instructions:
{task}
Use your own words. Do not copy long passages.
Do NOT mention activities, experiments, lab steps, or "Let us find out".
Do NOT list exercise questions or figure captions.
Do NOT repeat the same idea twice.
Do NOT use headings, bullet points, or numbered lists.

{SUMMARY_PROSE_INSTRUCTIONS.format(grade=grade)}"""
    return f"{GUIDED_SYSTEM_PROMPT.format(grade=grade)}\n\n{body}"


def build_fallback_prompt() -> str:
    """Return the fallback message when retrieval fails."""
    return FALLBACK_RESPONSE


def format_retrieved_chunks(chunks: list[str]) -> str:
    """Join retrieved chunks into a single context string."""
    if not chunks:
        return ""
    return "\n\n---\n\n".join(chunks)
