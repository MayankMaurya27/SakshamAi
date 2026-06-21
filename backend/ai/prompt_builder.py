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

SOLVER_SYSTEM_PROMPT = """You are a strict multiple-choice question solver.
Your ONLY task: read the context and output the letter (A, B, C, or D) of the correct option.
Rules:
- Output ONLY a single letter: A, B, C, or D.
- If the context does not support any option, output: NONE
- Do NOT write any explanation, reasoning, sentence, or extra text whatsoever.
Example output: B"""

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

QUIZ_JSON_OUTPUT_FORMAT = """Return ONLY a valid JSON object. Do not include any code fences, markdown tags, or prose.

CRITICAL JSON RULES:
- The "question" field must contain a complete query that ENDS with a question mark (?). Do NOT write statements, fill-in-the-blank prompts, or sentences ending with "...".
- The "options" field must contain ONLY the four choices (A, B, C, D).
- Do NOT swap or invert these fields (do not put choices in "question" or the query in "options").

JSON Format (containing exactly {question_count} question objects in the array):
{{
  "questions": [
    {{
      "question": "Question 1 text (must end with a question mark)?",
      "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
      }},
      "correct_answer": "A"
    }},
    {{
      "question": "Question 2 text (must end with a question mark)?",
      "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
      }},
      "correct_answer": "B"
    }}
  ]
}}
"""

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

""" + QUIZ_JSON_OUTPUT_FORMAT,
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
Write 4 to 6 bullet points only.
Each bullet must be at most 12 words.
Use simple everyday words.
Keep NCERT terms but add a short meaning in brackets.
Do not write long paragraphs.

Example format:
• Photosynthesis (how plants make food) uses sunlight.
• Chlorophyll (green pigment) traps light energy.

Rules:
- One idea per bullet
- Short sentences only
- No story characters
- Use only facts from the context""",
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

""" + QUIZ_JSON_OUTPUT_FORMAT

SCIENCE_QUIZ_TEMPLATE = """Context:
{retrieved_context}

{chapter_section}Instructions:
Generate exactly {question_count} multiple-choice science questions for Class {grade}.

Question style:
- Ask about facts, definitions, processes, and concepts from the chapter.
- Each question must be a clear factual MCQ with one correct answer.
- Every question must be a complete query ending with a question mark (?). Do NOT write fill-in-the-blank statements ending with "...".
- Keep each question under 140 characters.
- Do NOT copy rhetorical questions, activity instructions, or textbook introductions.
- Do NOT paste long sentences from the context as the question.
- Use simple English suitable for Class {grade}.

Options:
- Four distinct answer choices.
- Only one correct option.
- Vary correct_answer across A, B, C, and D.

""" + QUIZ_JSON_OUTPUT_FORMAT

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

    # Social Science template routing
    sub_lower = (subject or "").lower()
    if any(term in sub_lower for term in ("social", "history", "geography", "civics", "political", "economics")):
        chapter_section = f"Chapter:\n{topic}\n\n" if topic else ""
        body = SOCIAL_SCIENCE_QUIZ_TEMPLATE.format(
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


CONCEPT_EXTRACTION_PROMPT = """You are Saksham AI, an offline educational assistant. Extract the core educational concepts from the textbook context below.

Context:
{retrieved_context}

{chapter_section}Instructions:
- Extract exactly {concept_count} key educational concepts.
- For each concept, provide a 'concept_name' (clear, short name) and a 'concept_description' (1-2 sentences explaining the core factual concept details from the text).
- Do NOT include activity steps, mapping instructions, figure descriptions, or side notes.
- Return ONLY valid JSON with a "concepts" array. Do not use code fences or prose.

JSON Format (containing exactly {concept_count} concept objects in the array):
{{
  "concepts": [
    {{
      "concept_name": "Name of first concept",
      "concept_description": "Description of the first key educational facts from the text."
    }},
    {{
      "concept_name": "Name of second concept",
      "concept_description": "Description of the second key educational facts from the text."
    }}
  ]
}}"""

CONCEPT_QUIZ_TEMPLATE = """Context:
{retrieved_context}

{chapter_section}Concepts to test:
{concepts_list}

Instructions:
Generate exactly {question_count} multiple-choice questions for Class {grade}. Each question must test one of the key concepts listed above.

Question style:
- Test conceptual understanding of the targeted concept.
- Write an actual, natural question ending with a question mark.
- Do NOT copy the concept name or concept description verbatim as the question.
- Do NOT use activity instructions, mapping tasks, or rhetorical questions.
- Keep each question under 140 characters and grammatically complete.
- Options must be distinct, plausible, and complete options (no fragments).
- Only one option must be correct.

""" + QUIZ_JSON_OUTPUT_FORMAT

SOCIAL_SCIENCE_QUIZ_TEMPLATE = """Context:
{retrieved_context}

{chapter_section}Instructions:
Generate exactly {question_count} multiple-choice social science (history, geography, civics, or economics) questions for Class {grade}.

Question style:
- Ask about facts, definitions, causes, historical/geographical concepts, and processes from the chapter.
- Each question must be a clear factual MCQ with one correct answer.
- Every question must be a complete query ending with a question mark (?). Do NOT write fill-in-the-blank statements ending with "...".
- Keep each question under 140 characters.
- Do NOT copy rhetorical questions, activity instructions, or map reading tasks.
- Do NOT paste long sentences from the context as the question.
- Use simple English suitable for Class {grade}.

Options:
- Four distinct, complete answer choices. No sentence fragments.
- Only one correct option.
- Vary correct_answer across A, B, C, and D.

""" + QUIZ_JSON_OUTPUT_FORMAT


def build_concept_extraction_prompt(
    retrieved_context: str,
    topic: str = "",
    concept_count: int = 5,
) -> str:
    """Build a prompt to extract core concepts from a chapter context."""
    chapter_section = f"Chapter:\n{topic}\n\n" if topic else ""
    body = CONCEPT_EXTRACTION_PROMPT.format(
        retrieved_context=retrieved_context,
        chapter_section=chapter_section,
        concept_count=concept_count,
    )
    return f"{STRICT_SYSTEM_PROMPT}\n\n{body}"


def build_concept_quiz_prompt(
    retrieved_context: str,
    concepts_list: str,
    question_count: int,
    topic: str = "",
    grade: int = 8,
) -> str:
    """Build a prompt to generate concept-targeted quiz questions."""
    chapter_section = f"Chapter:\n{topic}\n\n" if topic else ""
    body = CONCEPT_QUIZ_TEMPLATE.format(
        retrieved_context=retrieved_context,
        chapter_section=chapter_section,
        concepts_list=concepts_list,
        question_count=question_count,
        grade=grade,
    )
    return f"{STRICT_SYSTEM_PROMPT}\n\n{body}"


SUMMARY_PROSE_INSTRUCTIONS = """Output format (plain text only — do NOT use JSON, headings, or bullet lists):
Write a detailed revision summary of about {target_words} words for a Class {grade} student.
Use at least {min_paragraphs} paragraphs. Add more paragraphs if the context covers many ideas.
Each paragraph should be 3-5 sentences and cover a distinct part of the chapter.
Separate each paragraph with one blank line."""


def build_summary_prompt(
    retrieved_context: str,
    topic: str = "",
    grade: int = 8,
    window_hint: str = "",
    mode: str = "full",
    target_words: int = 380,
    min_paragraphs: int = 4,
) -> str:
    """Build a plain-text chapter/document summary prompt for the local LLM."""
    chapter_section = f"Chapter:\n{topic}\n\n" if topic else ""
    hint = f"{window_hint}\n\n" if window_hint else ""

    if mode == "partial":
        task = (
            "Write detailed revision notes for this section of the chapter using ONLY the context above. "
            "Use at least 3-4 paragraphs and about "
            f"{max(160, target_words // 2)} words. "
            "Cover every main idea in this section. This is one part of a longer chapter."
        )
    elif mode == "synthesis":
        task = (
            "Combine the partial revision notes below into one complete chapter summary. "
            f"Use at least {min_paragraphs + 1} paragraphs and about {target_words} words. "
            "Include all important ideas from the notes. Remove repetition and keep the flow easy to read."
        )
    elif mode == "expand":
        task = (
            "The draft summary below is too short. Expand it into a complete chapter revision summary "
            f"of about {target_words} words in at least {min_paragraphs} paragraphs. "
            "Add missing main ideas from the source context. Keep the draft's correct facts, but add more detail."
        )
    else:
        task = (
            "Write a complete revision summary for the full chapter using ONLY the context above. "
            f"Use at least {min_paragraphs} paragraphs and about {target_words} words. "
            "Cover all major sections, definitions, and key ideas from the chapter."
        )

    body = f"""Context:
{retrieved_context}

{chapter_section}{hint}Instructions:
{task}
Use your own words. Do not copy long passages.
Use ONLY facts that appear in the context. Do NOT add outside knowledge.
Do NOT mention story characters (Bhavisha, Dhruv, Ira, Jonali, Pallabi, Arshad, Ajay).
Do NOT describe time machines, fictional travel, or story plots.
Do NOT treat textbook story characters as real historical people.
Do NOT mention activities, experiments, lab steps, or "Let us find out".
Do NOT list exercise questions or figure captions.
Do NOT repeat the same idea twice.
Do NOT use headings, bullet points, or numbered lists.

{SUMMARY_PROSE_INSTRUCTIONS.format(grade=grade, target_words=target_words, min_paragraphs=min_paragraphs)}"""
    return f"{GUIDED_SYSTEM_PROMPT.format(grade=grade)}\n\n{body}"


def build_summary_expand_prompt(
    draft_summary: str,
    retrieved_context: str,
    topic: str = "",
    grade: int = 8,
    target_words: int = 380,
    min_paragraphs: int = 4,
) -> str:
    """Ask the LLM to expand a short draft using the source context."""
    chapter_section = f"Chapter:\n{topic}\n\n" if topic else ""
    body = f"""Draft summary (too short):
{draft_summary.strip()}

Source context:
{retrieved_context}

{chapter_section}Instructions:
Expand the draft into a complete revision summary of about {target_words} words.
Use at least {min_paragraphs} paragraphs separated by blank lines.
Add missing main ideas from the source context only.
Use ONLY facts supported by the source context.
Do NOT mention story characters, time machines, or fictional narratives.
Do NOT use headings, bullet points, or numbered lists.

{SUMMARY_PROSE_INSTRUCTIONS.format(grade=grade, target_words=target_words, min_paragraphs=min_paragraphs)}"""
    return f"{GUIDED_SYSTEM_PROMPT.format(grade=grade)}\n\n{body}"


def build_fallback_prompt() -> str:
    """Return the fallback message when retrieval fails."""
    return FALLBACK_RESPONSE


def format_retrieved_chunks(chunks: list[str]) -> str:
    """Join retrieved chunks into a single context string."""
    if not chunks:
        return ""
    return "\n\n---\n\n".join(chunks)


def build_solve_prompt(
    context: str,
    question: str,
    options: dict[str, str],
) -> str:
    """Build a prompt asking the LLM to solve the MCQ and output the correct option letter."""
    options_str = "\n".join(f"{k}: {v}" for k, v in options.items())
    body = f"""Context:
{context}

Question:
{question}

Options:
{options_str}

Answer (output ONLY the letter A, B, C, D, or NONE):"""
    return f"{SOLVER_SYSTEM_PROMPT}\n\n{body}"
