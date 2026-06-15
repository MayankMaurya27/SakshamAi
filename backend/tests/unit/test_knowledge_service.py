"""Unit tests for knowledge service."""

from config.settings import Settings
from services.knowledge_service import (
    _is_deployable_without_pdf,
    compute_curriculum_hash,
    list_chapters,
    list_classes,
    list_subjects,
    load_manifest,
)
from services.curriculum_utils import discover_chapter_pdfs


def test_class8_science_curriculum_available():
    """Class 8 Science should be available via manifest or PDFs."""
    settings = Settings()
    pdf_chapters = discover_chapter_pdfs(settings.saksham_kb_dir)
    science_8_pdfs = [c for c in pdf_chapters if c.class_level == 8 and c.subject == "Science"]
    science_8_manifest = list_chapters(8, "Science")
    assert len(science_8_pdfs) >= 13 or len(science_8_manifest) >= 13


def test_manifest_or_discover():
    """Manifest or PDF discovery should list Class 8 Science chapters."""
    manifest = load_manifest()
    chapters = manifest.get("chapters", [])
    science_8_manifest = [
        c for c in chapters if c.get("class") == 8 and c.get("subject") == "Science"
    ]
    if science_8_manifest:
        assert len(science_8_manifest) >= 13
    else:
        listed = list_chapters(8, "Science")
        assert len(listed) >= 13


def test_list_taxonomy_from_manifest():
    """Taxonomy should include Class 8 Science when PDFs are present."""
    classes = list_classes()
    assert 8 in classes

    subjects = list_subjects(8)
    assert "Science" in subjects

    chapters = list_chapters(8, "Science")
    assert len(chapters) >= 13
    assert all("chapter_id" in c and "chapter_title" in c for c in chapters)


def test_curriculum_hash_stable():
    """Curriculum hash should be stable for unchanged PDFs."""
    hash1 = compute_curriculum_hash()
    hash2 = compute_curriculum_hash()
    assert hash1 == hash2
    assert len(hash1) == 64


def test_deployable_without_pdf_all_classes():
    """Classes 6–10 manifest chapters are deployable without source PDFs."""
    assert _is_deployable_without_pdf({"class": 6, "subject": "Science", "chapter_id": "x"})
    assert _is_deployable_without_pdf({"class": 10, "subject": "Economics", "chapter_id": "y"})
    assert not _is_deployable_without_pdf({"class": 6, "subject": "Science", "legacy_json": True})
    assert not _is_deployable_without_pdf({"class": 5, "subject": "Science", "chapter_id": "z"})
