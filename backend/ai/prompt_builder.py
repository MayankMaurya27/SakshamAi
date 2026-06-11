"""Centralized prompt template construction and routing."""

from config.constants import LearningMode

GLOBAL_SYSTEM_PROMPT = """You are Saksham AI, an offline educational learning companion.

Your responsibilities:
- Explain educational concepts clearly
- Use only the provided context
- Help students understand topics
- Avoid making up information
- Prefer short and accurate answers
- Be friendly and educational

If the answer is not present in the context, state that the information was not found."""

FALLBACK_RESPONSE = (
    "The required information was not found in the available educational content. "
    "Please upload a relevant document or choose another topic."
)

TEMPLATES: dict[LearningMode, str] = {
    LearningMode.LEARN: """Context:
{retrieved_context}

Question:
{question}

Instructions:
Explain the concept clearly.
Use educational language.
Keep the answer concise.
Provide examples if useful.
Do not invent information.""",
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
    LearningMode.LEARN_FROM_SAKSHAM: """Topic:
{topic}

Knowledge:
{retrieved_context}

Instructions:
Teach the topic clearly.
Provide:
1. Definition
2. Explanation
3. Example
4. Quick Revision Point

Suitable for Class {grade} students.""",
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

    body = template.format(
        retrieved_context=retrieved_context,
        question=question,
        document_text=document_text,
        topic=topic,
        grade=grade,
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
