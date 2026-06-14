"""Unit tests for factual summary filtering."""

from services.summary_factual import (
    ground_summary_text,
    is_narrative_sentence,
    strip_narrative_sentences,
)

EMPIRE_CHUNK = (
    "Bhavisha and Dhruv were thrilled; they had just activated their new device, "
    "'Itihāsa', a time machine to travel to the past! "
    "My name is Ira, daughter of Kanhadas, the ironsmith. Welcome to Pāṭaliputra! "
    "What is an Empire? The word 'empire' comes from the Latin 'imperium', which means "
    "'supreme power'. Simply put, an empire is a collection of smaller kingdoms or territories "
    "over which a powerful ruler or group of rulers exert power. "
    "Tributary: A tributary is a ruler or state that has submitted to an emperor and pays tribute."
)

BAD_SUMMARY = (
    "Life in ancient India was different from today, and every village had its own ruler or king.\n\n"
    "The people of Pataliputra were ruled by a powerful king named Bhavisha and Dhruv. "
    "They had just activated their time machine, Itihāsa.\n\n"
    "Simply put, an empire is a collection of smaller kingdoms or territories over which "
    "a powerful ruler exerts power. A tributary is a ruler or state that pays tribute to an emperor."
)


def test_strip_narrative_sentences_keeps_definitions():
    cleaned = strip_narrative_sentences(EMPIRE_CHUNK)
    assert "Bhavisha" not in cleaned
    assert "Ira" not in cleaned
    assert "imperium" in cleaned.lower()
    assert "tributary" in cleaned.lower()


def test_is_narrative_sentence_detects_story_content():
    assert is_narrative_sentence("Bhavisha and Dhruv activated their time machine.")
    assert not is_narrative_sentence(
        "Simply put, an empire is a collection of smaller kingdoms or territories."
    )


def test_ground_summary_text_removes_hallucinations_and_story():
    grounded = ground_summary_text(BAD_SUMMARY, EMPIRE_CHUNK)
    assert "Bhavisha" not in grounded
    assert "time machine" not in grounded.lower()
    assert "every village had its own ruler" not in grounded.lower()
    assert "empire is a collection of smaller kingdoms" in grounded.lower()
