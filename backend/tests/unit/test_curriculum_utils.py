"""Unit tests for curriculum utilities."""

from pathlib import Path

from services.curriculum_utils import (
    chapter_matches,
    discover_chapter_pdfs,
    slugify,
    title_from_filename,
)


def test_slugify():
    """Slugify should normalize filenames."""
    assert slugify("Exploring Forces.pdf") == "exploring_forces"
    assert slugify("Electricity- Magnetic and Heating Effects.pdf") == "electricity_magnetic_and_heating_effects"


def test_title_from_filename():
    """Title should strip extension."""
    assert title_from_filename("Exploring Forces.pdf") == "Exploring Forces"


def test_chapter_matches():
    """Chapter matching should accept id or title."""
    meta = {
        "class": 8,
        "subject": "Science",
        "chapter_id": "exploring_forces",
        "chapter_title": "Exploring Forces",
    }
    assert chapter_matches(meta, 8, "Science", "exploring_forces")
    assert chapter_matches(meta, 8, "Science", "Exploring Forces")
    assert not chapter_matches(meta, 8, "Science", "Electricity")


def test_discover_chapter_pdfs():
    """Should discover Class 8 Science PDF chapters."""
    kb_dir = Path(__file__).resolve().parent.parent.parent / "data" / "saksham_kb"
    chapters = discover_chapter_pdfs(kb_dir)
    science_8 = [c for c in chapters if c.class_level == 8 and c.subject == "Science"]
    assert len(science_8) >= 13
