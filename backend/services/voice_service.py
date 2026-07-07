import logging
import re
import json
import difflib
from typing import Any

from ai.llm import get_llm
from services.knowledge_service import _manifest_chapters

logger = logging.getLogger(__name__)

VOICE_NLU_SYSTEM_PROMPT = """You are Saksham Voice Assistant NLU parser.
Your task is to analyze the student's spoken text and output a JSON block matching this schema:
{
  "intent": "set_context" | "generate_quiz" | "get_summary" | "ask_question" | "repeat" | "stop" | "next" | "back" | "select_option" | "unknown",
  "class_level": null,
  "subject": null,
  "chapter": null,
  "query": null
}

Rules:
- Output ONLY valid JSON. Do not include markdown code fences (like ```json), no other text.
- Valid subjects are: "Science", "Social Science", "Mathematics".
- If the student asks a question about curriculum content (e.g. "what is photosynthesis", "why did Shunga perform yajna"), set intent to "ask_question" and put the question text into the "query" field.
- If the student selects an option (e.g. "Option A", "select A", "A"), set intent to "select_option" and put "A", "B", "C", or "D" in the "query" field.
"""

def _match_chapter_fuzzy(transcript: str, class_level: int | None, subject: str | None) -> str | None:
    """Fuzzy match a spoken chapter name against manifest chapter titles."""
    chapters = _manifest_chapters()
    
    # Filter chapters by class and subject if provided
    candidates = []
    for c in chapters:
        if class_level is not None and c.get("class") != class_level:
            continue
        if subject is not None:
            chapter_sub = str(c.get("subject", "")).lower()
            req_sub = subject.lower()
            if req_sub == "social science" and chapter_sub in {"history", "geography", "political science", "economics", "social science"}:
                subject_matched = True
            else:
                subject_matched = (chapter_sub == req_sub)
            if not subject_matched:
                continue
        candidates.append(c.get("chapter_title", ""))
        
    if not candidates:
        candidates = [c.get("chapter_title", "") for c in chapters]
        
    transcript_clean = transcript.lower().strip()
    
    # Check for direct substring match first
    for title in candidates:
        if title.lower() in transcript_clean or transcript_clean in title.lower():
            return title
            
    # Fuzzy match using difflib with a safer cutoff (0.55) to avoid false matches
    matches = difflib.get_close_matches(transcript, candidates, n=1, cutoff=0.55)
    if matches:
        return matches[0]
        
    return None

def parse_transcript(
    transcript: str,
    current_class: int | None = None,
    current_subject: str | None = None,
    current_chapter: str | None = None,
) -> dict[str, Any]:
    """Parse spoken student transcript to detect intent and parameters."""
    text = transcript.strip().lower()
    if not text:
        return {"intent": "unknown", "class_level": None, "subject": None, "chapter": None, "query": None}
        
    # --- STEP 1: Procedural / Regex Parsing ---
    
    # 1. Stop / Cancel
    if re.search(r"\b(stop|cancel|exit|shut\s*up|quit|go\s*away)\b", text):
        return {"intent": "stop", "class_level": None, "subject": None, "chapter": None, "query": None}
        
    # 2. Repeat
    if re.search(r"\b(repeat|read\s*(it\s*)?again|say\s*(that\s*|it\s*)?again|once\s*more)\b", text):
        return {"intent": "repeat", "class_level": None, "subject": None, "chapter": None, "query": None}
        
    # 3. Next / Back navigation
    if re.search(r"\b(next|continue|move\s*on|skip)\b", text):
        return {"intent": "next", "class_level": None, "subject": None, "chapter": None, "query": None}
    if re.search(r"\b(back|go\s*back|previous)\b", text):
        return {"intent": "back", "class_level": None, "subject": None, "chapter": None, "query": None}
        
    # 4. MCQ Option selection
    opt_match = re.search(r"\b(option|choice|answer\s*is|select)?\s*\b([a-d])\b", text)
    if opt_match and len(text.split()) <= 3:
        return {
            "intent": "select_option",
            "class_level": None,
            "subject": None,
            "chapter": None,
            "query": opt_match.group(2).upper()
        }

    # 5. Question check (If it starts with a question word, bypass context changes and route as a question)
    if re.match(r"^(what|why|how|who|when|where|explain|describe|tell me about|is there|are there|can you|could you)\b", text):
        return {
            "intent": "ask_question",
            "class_level": current_class,
            "subject": current_subject,
            "chapter": current_chapter,
            "query": transcript
        }
        
    # 6. Intent triggers (Quiz / Summary)
    is_quiz = re.search(r"\b(quiz|test|mcq|practice\s*questions)\b", text)
    is_summary = re.search(r"\b(summary|summarize|revision\s*notes|notes)\b", text)
    
    # 7. Extract class level
    class_level = current_class
    # Try digit-based matching first: e.g. class 9, class 9th, 9th, 9, etc.
    class_match = re.search(r"\b(class|grade|standard)?\s*(6|7|8|9|10)(st|nd|rd|th)?\b", text)
    if class_match:
        class_level = int(class_match.group(2))
    else:
        # Check text word representations
        words_map = {
            "sixth": 6, "six": 6,
            "seventh": 7, "seven": 7,
            "eighth": 8, "eight": 8,
            "ninth": 9, "nine": 9,
            "tenth": 10, "ten": 10
        }
        for word, val in words_map.items():
            if re.search(r"\b" + word + r"\b", text):
                class_level = val
                break
    
    # 8. Extract subject
    subject = current_subject
    if any(s in text for s in ["social science", "social studies", "history", "geography", "civics", "economics", "political science", "sst", "social"]):
        subject = "Social Science"
    elif "science" in text:
        subject = "Science"
    elif any(m in text for m in ["math", "maths", "mathematics"]):
        subject = "Mathematics"
        
    # 9. Extract chapter if explicitly spoken (fuzzy lookup)
    chapter = current_chapter
    clean_text_for_chapter = re.sub(r"\b(class\s*\d+|science|social science|geography|history|civics|economics|math|mathematics|quiz|summary|learn|ask)\b", "", text).strip()
    if len(clean_text_for_chapter) > 3:
        matched = _match_chapter_fuzzy(clean_text_for_chapter, class_level, subject)
        if matched:
            chapter = matched

    # If the user speaks class/subject/chapter, we set context
    context_changed = (class_level != current_class) or (subject != current_subject) or (chapter != current_chapter)
    
    if context_changed:
        intent = "set_context"
        if is_quiz:
            intent = "generate_quiz"
        elif is_summary:
            intent = "get_summary"
        return {
            "intent": intent,
            "class_level": class_level,
            "subject": subject,
            "chapter": chapter,
            "query": None
        }
        
    if is_quiz:
        return {"intent": "generate_quiz", "class_level": class_level, "subject": subject, "chapter": chapter, "query": None}
    if is_summary:
        return {"intent": "get_summary", "class_level": class_level, "subject": subject, "chapter": chapter, "query": None}

    # --- STEP 2: LLM Fallback Parsing for Conversational Queries ---
    
    logger.info("Voice parse: procedural rules did not match. Falling back to LLM.")
    prompt = f"{VOICE_NLU_SYSTEM_PROMPT}\n\nTranscript to parse: '{transcript}'\nCurrent context: Class {current_class}, Subject {current_subject}, Chapter {current_chapter}"
    
    try:
        response_text = get_llm().generate(prompt)
        response_text_clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", response_text.strip(), flags=re.I)
        parsed = json.loads(response_text_clean)
        
        intent = parsed.get("intent", "unknown")
        llm_class = parsed.get("class_level")
        llm_subject = parsed.get("subject")
        llm_chapter = parsed.get("chapter")
        query = parsed.get("query")
        
        if isinstance(llm_class, (int, float)):
            class_level = int(llm_class)
        if llm_subject in {"Science", "Social Science", "Mathematics"}:
            subject = llm_subject
        if llm_chapter:
            matched = _match_chapter_fuzzy(llm_chapter, class_level, subject)
            if matched:
                chapter = matched
                
        return {
            "intent": intent,
            "class_level": class_level,
            "subject": subject,
            "chapter": chapter,
            "query": query
        }
    except Exception as e:
        logger.error("LLM voice parsing fallback failed: %s. Defaulting to ask_question.", e)
        return {
            "intent": "ask_question",
            "class_level": current_class,
            "subject": current_subject,
            "chapter": current_chapter,
            "query": transcript
        }
