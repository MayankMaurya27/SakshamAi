"""Utilities for Saksham curriculum PDF discovery and naming."""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ChapterInfo:
    """Metadata for a curriculum chapter PDF."""

    class_level: int
    subject: str
    chapter_id: str
    chapter_title: str
    source_file: str
    pdf_path: Path


def slugify(text: str) -> str:
    """Convert text to a URL-safe chapter identifier."""
    text = Path(text).stem if text.lower().endswith(".pdf") else text
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text.strip("_")


def normalize_subject(folder_name: str) -> str:
    """Convert folder name to display subject (e.g. science -> Science)."""
    return folder_name.replace("_", " ").strip().title()


def title_from_filename(filename: str) -> str:
    """Derive human-readable chapter title from PDF filename."""
    return Path(filename).stem.strip()


# User-facing names that should map to a different indexed chapter (misnamed PDFs, etc.).
CHAPTER_ALIASES: dict[tuple[int, str, str], str] = {
    # Atomic Structure.pdf contains the grade-9 science intro ("Exploration"), not atoms.
    # Students asking for "Atomic Structure" expect Chapter 8: Journey Inside the Atom.
    (9, "science", "atomic structure"): "journey_inside_atoms",
    (9, "science", "atomic_structure"): "journey_inside_atoms",
}


def resolve_chapter_ref(class_level: int, subject: str, chapter_ref: str) -> str:
    """Map common chapter names to the indexed chapter_id when PDF names differ."""
    ref = chapter_ref.strip()
    if not ref:
        return ref

    subject_key = subject.strip().lower()
    for key in (
        (class_level, subject_key, ref.lower()),
        (class_level, subject_key, slugify(ref)),
    ):
        target = CHAPTER_ALIASES.get(key)
        if target:
            return target
    return ref


def chapter_matches(meta: dict, class_level: int, subject: str, chapter_ref: str) -> bool:
    """Return True if metadata matches class, subject, and chapter reference."""
    if meta.get("class") != class_level:
        return False
    if meta.get("subject", "").lower() != subject.lower():
        return False

    ref = chapter_ref.strip().lower()
    chapter_id = meta.get("chapter_id", "").lower()
    chapter_title = meta.get("chapter_title", "").lower()
    topic = meta.get("topic", "").lower()
    ref_slug = slugify(chapter_ref)

    return (
        ref in {chapter_id, chapter_title, topic}
        or ref_slug == chapter_id
        or ref_slug == slugify(chapter_title)
    )


def _subject_from_path_parts(parts: tuple[str, ...]) -> str | None:
    """
    Resolve subject from a PDF path under class{N}/...

    Supports:
    - class8/science/Chapter.pdf -> Science
    - class8/social science/Chapter.pdf -> Social Science
    - class9/social science/history/Chapter.pdf -> History
    """
    if len(parts) < 2:
        return None

    subject_dir = parts[1].lower().replace("_", " ")
    if subject_dir == "social science" and len(parts) >= 4:
        return normalize_subject(parts[2])
    return normalize_subject(parts[1])


def discover_chapter_pdfs(kb_dir: Path) -> list[ChapterInfo]:
    """Discover chapter PDFs under class{N}/{subject}/*.pdf layout."""
    chapters: list[ChapterInfo] = []
    if not kb_dir.exists():
        return chapters

    for pdf_path in sorted(kb_dir.rglob("*.pdf")):
        relative = pdf_path.relative_to(kb_dir)
        parts = relative.parts
        if len(parts) < 3:
            continue

        class_dir = parts[0]
        if not class_dir.startswith("class"):
            continue

        try:
            class_level = int(class_dir.replace("class", ""))
        except ValueError:
            continue

        subject = _subject_from_path_parts(parts)
        if subject is None:
            continue

        filename = parts[-1]
        chapter_title = title_from_filename(filename)
        chapter_id = slugify(filename)

        chapters.append(
            ChapterInfo(
                class_level=class_level,
                subject=subject,
                chapter_id=chapter_id,
                chapter_title=chapter_title,
                source_file=filename,
                pdf_path=pdf_path,
            )
        )

    return chapters
