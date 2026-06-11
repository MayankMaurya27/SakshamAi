"""Unit tests for textbook reference extraction and retrieval boosting."""

from ai.retriever import (
    _extract_activity_passage,
    _extract_focused_snippet,
    extract_content_refs,
    extract_query_terms,
    _is_low_quality_chunk,
    _keyword_match_score,
)


def test_extract_content_refs_activity():
    """Should extract activity references from questions."""
    refs = extract_content_refs("Explain activity 10.2")
    assert "Activity 10.2" in refs
    assert "10.2" not in refs


def test_extract_content_refs_figure():
    """Should extract figure references from questions."""
    refs = extract_content_refs("What does Fig. 10.4 show?")
    assert "Fig. 10.4" in refs


def test_is_low_quality_chunk_footer():
    """Page footers with dot leaders should be filtered."""
    footer = "so far ... " + "." * 200
    assert _is_low_quality_chunk(footer)


def test_keyword_match_score_prefers_activity():
    """Activity references should outrank bare section numbers."""
    text = "Activity 10.2: Let us distinguish concave and convex mirrors."
    refs = extract_content_refs("Explain activity 10.2")
    assert _keyword_match_score(text, refs) >= 3.0


def test_extract_activity_passage_across_chunks():
    """Activity text split across chunks should be stitched together."""
    chunks = [
        (0, "Earlier topic about straps. Activity 6.1: Let us try pipes and balloons.", 1),
        (1, "Both balloons bulge the same. Activity 6.2: Next experiment begins here.", 2),
    ]
    passage = _extract_activity_passage(chunks, "Activity 6.1")
    assert passage is not None
    assert "pipes and balloons" in passage
    assert "Both balloons bulge the same" in passage
    assert "Activity 6.2" not in passage


def test_extract_focused_snippet_centers_on_activity():
    """Snippet extraction should center on the referenced activity."""
    text = "A" * 2000 + "Activity 6.1: balloon experiment" + "B" * 500
    snippet = _extract_focused_snippet(text, ["Activity 6.1"])
    assert "Activity 6.1" in snippet
    assert len(snippet) < len(text)


def test_extract_query_terms_from_who_was_question():
    """Who-was questions should yield the person's name."""
    terms = extract_query_terms("who was Meghnad Saha")
    assert "Meghnad Saha" in terms
