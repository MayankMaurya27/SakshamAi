"""Unit tests for Voice Assistant NLU parsing."""

from unittest.mock import MagicMock, patch
from services.voice_service import parse_transcript, _match_chapter_fuzzy

def test_procedural_commands():
    # Stop intent
    res = parse_transcript("please stop now")
    assert res["intent"] == "stop"
    
    # Repeat intent
    res = parse_transcript("can you say that again")
    assert res["intent"] == "repeat"
    
    # Next / Back intents
    res = parse_transcript("go to the next question")
    assert res["intent"] == "next"
    res = parse_transcript("go back please")
    assert res["intent"] == "back"
    
    # Select Option intent
    res = parse_transcript("Option A")
    assert res["intent"] == "select_option"
    assert res["query"] == "A"
    
    res = parse_transcript("select b")
    assert res["intent"] == "select_option"
    assert res["query"] == "B"

def test_context_triggers():
    # Set class and subject
    res = parse_transcript("switch to class 9 science")
    assert res["intent"] == "set_context"
    assert res["class_level"] == 9
    assert res["subject"] == "Science"
    
    # Class 9th
    res = parse_transcript("class 9th")
    assert res["intent"] == "set_context"
    assert res["class_level"] == 9
    
    # Class nine
    res = parse_transcript("class nine")
    assert res["intent"] == "set_context"
    assert res["class_level"] == 9
    
    # 9th class
    res = parse_transcript("9th class")
    assert res["intent"] == "set_context"
    assert res["class_level"] == 9
    
    # Class 10th
    res = parse_transcript("class 10th")
    assert res["intent"] == "set_context"
    assert res["class_level"] == 10

    # sst subject
    res = parse_transcript("switch to sst", current_class=9)
    assert res["intent"] == "set_context"
    assert res["subject"] == "Social Science"

    # maths subject
    res = parse_transcript("switch to maths", current_class=9)
    assert res["intent"] == "set_context"
    assert res["subject"] == "Mathematics"

    # Generate quiz trigger
    res = parse_transcript("class 9 geography generate quiz")
    assert res["intent"] == "generate_quiz"
    assert res["class_level"] == 9
    assert res["subject"] == "Social Science"
    
    # Get summary trigger
    res = parse_transcript("read summary")
    assert res["intent"] == "get_summary"

def test_chapter_fuzzy_matching():
    # Check fuzzy matching for "palanpur" -> "The Story of Village Palampur"
    matched = _match_chapter_fuzzy("village palanpur", class_level=9, subject="Economics")
    assert matched == "The Story of Village Palampur"
    
    # Check fuzzy matching for "climate" -> "CLIMATE"
    matched = _match_chapter_fuzzy("climates", class_level=9, subject="Geography")
    assert matched == "CLIMATE"

@patch("services.voice_service.get_llm")
def test_llm_fallback(mock_get_llm):
    # Mock LLM response to return a valid JSON block
    mock_client = MagicMock()
    mock_client.generate.return_value = '{"intent": "ask_question", "class_level": 9, "subject": "Geography", "chapter": "CLIMATE", "query": "what are western disturbances"}'
    mock_get_llm.return_value = mock_client
    
    res = parse_transcript(
        "what are western disturbances",
        current_class=9,
        current_subject="Social Science",
        current_chapter="CLIMATE"
    )
    
    assert res["intent"] == "ask_question"
    assert res["query"] == "what are western disturbances"
    assert res["class_level"] == 9
    assert res["subject"] == "Social Science"
    assert res["chapter"] == "CLIMATE"
