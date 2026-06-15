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


def test_get_chapter_from_manifest_does_not_match_unrelated_chapters():
    """Slugified ref must match the chapter, not every chapter in the class."""
    from services.knowledge_service import get_chapter_from_manifest

    chapter = get_chapter_from_manifest(10, "Science", "Electricity")
    assert chapter is not None
    assert chapter["chapter_id"] == "electricity"
    assert chapter["chapter_title"] == "Electricity"


def test_resolve_chapter_ref_atomic_structure_alias():
    """Misnamed Atomic Structure.pdf should resolve to Journey Inside the Atom."""
    from services.curriculum_utils import resolve_chapter_ref
    from services.knowledge_service import get_chapter_from_manifest

    assert resolve_chapter_ref(9, "Science", "Atomic Structure") == "journey_inside_atoms"
    chapter = get_chapter_from_manifest(9, "Science", "Atomic Structure")
    assert chapter is not None
    assert chapter["chapter_id"] == "journey_inside_atoms"


def test_discover_chapter_pdfs():
    """Should discover chapter PDFs when present, or rely on manifest when PDF-free."""
    kb_dir = Path(__file__).resolve().parent.parent.parent / "data" / "saksham_kb"
    chapters = discover_chapter_pdfs(kb_dir)
    if chapters:
        assert len(chapters) >= 100
    else:
        from services.knowledge_service import load_manifest

        assert len(load_manifest().get("chapters", [])) >= 100


def test_discover_nested_social_science_subjects():
    """Class 9/10 social science PDFs in subfolders should map to History, etc."""
    kb_dir = Path(__file__).resolve().parent.parent.parent / "data" / "saksham_kb"
    chapters = discover_chapter_pdfs(kb_dir)

    if not chapters:
        from services.knowledge_service import list_chapters

        assert len(list_chapters(9, "History")) >= 1
        assert len(list_chapters(10, "Economics")) >= 1
        assert len(list_chapters(6, "Social Science")) >= 1
        return

    history_9 = [c for c in chapters if c.class_level == 9 and c.subject == "History"]
    economics_10 = [c for c in chapters if c.class_level == 10 and c.subject == "Economics"]
    social_6 = [c for c in chapters if c.class_level == 6 and c.subject == "Social Science"]

    assert len(history_9) >= 1
    assert len(economics_10) >= 1
    assert len(social_6) >= 1
    assert not any(
        c.class_level in (9, 10) and c.subject == "Social Science"
        for c in chapters
        if "social science" in str(c.pdf_path).lower()
        and len(c.pdf_path.relative_to(kb_dir).parts) >= 4
    )
