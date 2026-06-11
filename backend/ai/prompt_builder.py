"""Centralized prompt template construction and routing."""

from config.constants import LearningMode

GLOBAL_SYSTEM_PROMPT = """You are Saksham AI, an offline educational assistant for Indian school students.

STRICT RULES:
- Use ONLY the provided context. Never add outside knowledge.
- Answer ONLY what the student asked. No full-chapter overviews unless requested.
- Start directly with the answer. No greetings or chatbot phrases.
- Never say: "Welcome", "I'd be happy to help", "The student asked", "According to the context", "Let me know if", "Let's move on", "Do you have any questions".
- Do not use a Definition / Explanation / Example / Quick Revision template unless the student explicitly asks for revision notes.
- Do not invent activities, figures, examples, or scientific claims.
- If the answer is not in the context, reply exactly: "This was not found in the chapter content."

Write in clear, simple English with short paragraphs and bullet points where helpful."""

FALLBACK_RESPONSE = (
    "The required information was not found in the available educational content. "
    "Please upload a relevant document or choose another topic."
)

TEMPLATES: dict[LearningMode, str] = {
    LearningMode.LEARN: """Context:
{retrieved_context}

{chapter_section}Question:
{question}

Instructions:
Answer the question directly and comprehensively using only the context.
Use clear paragraphs or bullet points where helpful.
Do not use Aim, Procedure, Observation, or Conclusion headings unless the question asks about a specific activity or figure.
Keep the answer focused on what was asked.
Do not add extra topics or revision sections.""",
    LearningMode.SIMPLIFY: """Context:
{retrieved_context}

Question:
{question}

Instructions:
Explain as if teaching a Class 6 student.
Use simple words.
Use short sentences.
Use everyday examples.
Avoid technical jargon.
Do not add information not found in the context.""",
    LearningMode.HINDI: """Context:
{retrieved_context}

Question:
{question}

Instructions:
Explain in Hindi.
Keep educational terms accurate.
Use simple Hindi.
If an English scientific term is commonly used, include it in brackets.
Do not invent information.""",
    LearningMode.QUIZ: """Context:
{retrieved_context}

Instructions:
Generate 5 multiple-choice questions.
Each question must have:
- Question
- Four options (A, B, C, D)
- Correct answer

Questions must be based only on the provided context.
Return valid JSON with a "questions" array.""",
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
Avoid difficult vocabulary.""",
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
Provide concise answer optimized for audio narration.
Use short sections.
Avoid tables.
Avoid complex formatting.""",
    LearningMode.LEARN_FROM_SAKSHAM: """Context:
{retrieved_context}

Chapter:
{topic}

Question:
{question}

Instructions:
Answer the question directly and comprehensively using only the context. Class {grade} level.
Use clear paragraphs or bullet points. Do not use Aim, Procedure, Observation, or Conclusion headings.
Do not invent information. If the context lacks the answer: "This was not found in the chapter content.\"""",
}


def build_prompt(
    mode: LearningMode,
    retrieved_context: str = "",
    question: str = "",
    document_text: str = "",
    topic: str = "",
    grade: int = 8,
) -> str:
    """Build a complete prompt for the given learning mode."""
    template = TEMPLATES.get(mode)
    if template is None:
        raise ValueError(f"Unknown learning mode: {mode}")

    chapter_section = f"Chapter:\n{topic}\n\n" if topic else ""

    body = template.format(
        retrieved_context=retrieved_context,
        question=question,
        document_text=document_text,
        topic=topic,
        grade=grade,
        chapter_section=chapter_section,
    )
    return f"{GLOBAL_SYSTEM_PROMPT}\n\n{body}"


def build_fallback_prompt() -> str:
    """Return the fallback message when retrieval fails."""
    return FALLBACK_RESPONSE


def format_retrieved_chunks(chunks: list[str]) -> str:
    """Join retrieved chunks into a single context string."""
    if not chunks:
        return ""
    return "\n\n---\n\n".join(chunks)
