"""Unit tests for quiz context preparation."""

from services.quiz_context import (
    filter_quiz_source_chunks,
    is_exercise_list_chunk,
    prepare_quiz_context,
    stratified_sample_chunks,
)


def test_is_exercise_list_chunk_detects_numbered_exercises():
    text = (
        "5. Construct a table on land distribution. "
        "6. Why are wages less than minimum wages? "
        "7. In your region, talk to two labourers. "
        "8. What are the different ways of increasing production?"
    )
    assert is_exercise_list_chunk(text)


def test_filter_quiz_source_chunks_removes_exercise_block():
    chunks = [
        (
            "Farming is the main activity in Palampur and most families depend on it "
            "for their livelihood throughout the year."
        ),
        (
            "5. Construct a table. 6. Why are wages less than minimum wages? "
            "7. Talk to labourers. 8. Ways of increasing production."
        ),
    ]
    filtered = filter_quiz_source_chunks(chunks)
    assert len(filtered) == 1
    assert "Farming is the main activity" in filtered[0]


def test_stratified_sample_chunks_evenly_spreads():
    chunks = [f"chunk-{idx}" for idx in range(10)]
    sampled = stratified_sample_chunks(chunks, 5)
    assert len(sampled) == 5
    assert sampled[0] == "chunk-0"
    assert sampled[-1] == "chunk-9"


def test_prepare_quiz_context_respects_separator_budget():
    chunks = [f"Section {idx} " + ("word " * 200) for idx in range(12)]
    context = prepare_quiz_context(chunks, max_chars=1500)
    assert len(context) <= 1500

    chunks = [
        "Section one explains resources and development in detail for students.",
        "Section two explains land use planning with several important examples.",
    ]
    context = prepare_quiz_context(chunks, max_chars=5000)
    assert "Section one" in context
    assert "Section two" in context
