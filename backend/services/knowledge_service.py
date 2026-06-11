"""Saksham educational knowledge base and curriculum indexing."""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from ai.faiss_manager import FaissManager, get_saksham_index, reset_saksham_index, save_saksham_index
import ai.faiss_manager as faiss_manager_module
from config.settings import get_settings
from documents.chunker import create_chunks
from documents.indexer import index_document
from documents.pdf_parser import extract_text
from exceptions import ValidationError
from services.curriculum_utils import (
    ChapterInfo,
    chapter_matches,
    discover_chapter_pdfs,
    slugify,
)

logger = logging.getLogger(__name__)
settings = get_settings()


def manifest_path() -> Path:
    """Path to curriculum manifest JSON."""
    return settings.saksham_kb_dir / "manifest.json"


def load_manifest() -> dict[str, Any]:
    """Load curriculum manifest or return empty structure."""
    path = manifest_path()
    if not path.exists():
        return {"version": 1, "chapters": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(chapters: list[dict[str, Any]]) -> None:
    """Persist curriculum manifest."""
    path = manifest_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"version": 1, "chapters": chapters}
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Saved manifest with %d chapters to %s", len(chapters), path)


def compute_curriculum_hash() -> str:
    """Hash all curriculum PDFs for staleness detection."""
    hasher = hashlib.sha256()
    kb_dir = settings.saksham_kb_dir
    if not kb_dir.exists():
        return ""

    for pdf_file in sorted(kb_dir.rglob("*.pdf")):
        hasher.update(pdf_file.read_bytes())

    return hasher.hexdigest()


def _load_legacy_json_topics() -> list[dict[str, Any]]:
    """Load legacy JSON topic files (classes without PDF curriculum yet)."""
    topics: list[dict[str, Any]] = []
    kb_dir = settings.saksham_kb_dir
    if not kb_dir.exists():
        return topics

    pdf_chapter_ids = {
        (c.class_level, c.subject.lower(), c.chapter_id)
        for c in discover_chapter_pdfs(kb_dir)
    }

    for json_file in kb_dir.rglob("*.json"):
        if json_file.name == "manifest.json":
            continue
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            class_level = data.get("class")
            subject = data.get("subject", "")
            topic = data.get("topic", "")
            chapter_id = slugify(topic)
            if (class_level, subject.lower(), chapter_id) in pdf_chapter_ids:
                continue
            data["_file_path"] = str(json_file)
            topics.append(data)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load topic file %s: %s", json_file, exc)

    return topics


def ingest_chapter_pdf(chapter: ChapterInfo, saksham_index) -> dict[str, Any]:
    """Extract, chunk, and index a single chapter PDF."""
    text, page_count = extract_text(str(chapter.pdf_path))
    chunks = create_chunks(text)
    if not chunks:
        raise ValidationError(f"No chunks created from {chapter.source_file}")

    metadata_base = {
        "class": chapter.class_level,
        "subject": chapter.subject,
        "chapter_id": chapter.chapter_id,
        "chapter_title": chapter.chapter_title,
        "topic": chapter.chapter_title,
        "source_file": chapter.source_file,
        "source": "saksham_curriculum",
    }
    index_document(chunks, saksham_index, metadata_base=metadata_base)

    return {
        "class": chapter.class_level,
        "subject": chapter.subject,
        "chapter_id": chapter.chapter_id,
        "chapter_title": chapter.chapter_title,
        "source_file": chapter.source_file,
        "page_count": page_count,
        "word_count": len(text.split()),
        "chunk_count": len(chunks),
    }


def build_saksham_index(force: bool = False) -> None:
    """
    Build or rebuild saksham FAISS index from curriculum PDFs and legacy JSON topics.

    Skips rebuild if PDF hash unchanged and index exists (unless force=True).
    """
    current_hash = compute_curriculum_hash()
    hash_path = settings.saksham_kb_hash_path

    if not force and settings.saksham_index_path.exists() and current_hash:
        if hash_path.exists() and hash_path.read_text().strip() == current_hash:
            logger.info("Saksham curriculum index is up to date, skipping rebuild")
            return

    chapters = discover_chapter_pdfs(settings.saksham_kb_dir)
    legacy_topics = _load_legacy_json_topics()

    if not chapters and not legacy_topics:
        logger.warning("No curriculum PDFs or legacy JSON topics found to index")
        return

    reset_saksham_index()
    saksham_index = FaissManager(name="saksham_index")
    saksham_index.create_index()
    faiss_manager_module._saksham_index = saksham_index

    manifest_entries: list[dict[str, Any]] = []
    total_chunks = 0

    for chapter in chapters:
        try:
            entry = ingest_chapter_pdf(chapter, saksham_index)
            manifest_entries.append(entry)
            total_chunks += entry["chunk_count"]
            logger.info(
                "Indexed chapter: class=%s subject=%s chapter=%s chunks=%d",
                chapter.class_level,
                chapter.subject,
                chapter.chapter_title,
                entry["chunk_count"],
            )
        except Exception as exc:
            logger.error("Failed to index %s: %s", chapter.source_file, exc)

    for topic_data in legacy_topics:
        content = topic_data.get("content", "")
        if not content:
            continue
        topic = topic_data.get("topic", "")
        chunks = create_chunks(content)
        metadata_base = {
            "class": topic_data.get("class"),
            "subject": topic_data.get("subject", ""),
            "chapter_id": slugify(topic),
            "chapter_title": topic,
            "topic": topic,
            "source": "saksham_kb_legacy",
        }
        index_document(chunks, saksham_index, metadata_base=metadata_base)
        total_chunks += len(chunks)
        manifest_entries.append(
            {
                "class": topic_data.get("class"),
                "subject": topic_data.get("subject", ""),
                "chapter_id": slugify(topic),
                "chapter_title": topic,
                "source_file": topic_data.get("_file_path", ""),
                "chunk_count": len(chunks),
                "legacy_json": True,
            }
        )

    save_saksham_index()
    save_manifest(manifest_entries)
    if current_hash:
        hash_path.write_text(current_hash, encoding="utf-8")

    logger.info(
        "Built Saksham index: %d chapters, %d total chunks, %d vectors",
        len(manifest_entries),
        total_chunks,
        saksham_index.total_vectors,
    )


def _manifest_chapters() -> list[dict[str, Any]]:
    """Return chapters from manifest, or discover PDFs if manifest empty."""
    manifest = load_manifest()
    chapters = manifest.get("chapters", [])
    if chapters:
        return chapters
    return [
        {
            "class": c.class_level,
            "subject": c.subject,
            "chapter_id": c.chapter_id,
            "chapter_title": c.chapter_title,
            "source_file": c.source_file,
        }
        for c in discover_chapter_pdfs(settings.saksham_kb_dir)
    ]


def list_classes() -> list[int]:
    """Return available class levels from curriculum manifest."""
    classes = {c["class"] for c in _manifest_chapters() if c.get("class") is not None}
    return sorted(classes)


def list_subjects(class_level: int) -> list[str]:
    """Return subjects for a class level."""
    subjects = {
        c["subject"]
        for c in _manifest_chapters()
        if c.get("class") == class_level and c.get("subject")
    }
    return sorted(subjects)


def list_chapters(class_level: int, subject: str) -> list[dict[str, str]]:
    """Return chapters for a class and subject."""
    chapters = [
        {
            "chapter_id": c["chapter_id"],
            "chapter_title": c["chapter_title"],
        }
        for c in _manifest_chapters()
        if c.get("class") == class_level
        and c.get("subject", "").lower() == subject.lower()
        and c.get("chapter_id")
    ]
    return sorted(chapters, key=lambda x: x["chapter_title"])


def list_topics(class_level: int, subject: str) -> list[str]:
    """Return chapter titles (backward-compatible alias for list_chapters)."""
    return [c["chapter_title"] for c in list_chapters(class_level, subject)]


def get_chapter_from_manifest(
    class_level: int, subject: str, chapter_ref: str
) -> dict[str, Any] | None:
    """Find chapter metadata by id or title."""
    ref = chapter_ref.strip().lower()
    for chapter in _manifest_chapters():
        if chapter.get("class") != class_level:
            continue
        if chapter.get("subject", "").lower() != subject.lower():
            continue
        if ref in {
            chapter.get("chapter_id", "").lower(),
            chapter.get("chapter_title", "").lower(),
            slugify(chapter_ref),
        }:
            return chapter
    return None


def get_chapter_chunk_texts(
    class_level: int, subject: str, chapter_ref: str
) -> list[str]:
    """Return all chunk texts for a chapter from FAISS metadata (direct lookup)."""
    saksham_index = get_saksham_index()
    chunks: list[tuple[int, str]] = []

    for faiss_id, meta in saksham_index.id_map.items():
        if not chapter_matches(meta, class_level, subject, chapter_ref):
            continue
        chunk_text = meta.get("chunk_text", "")
        chunk_index = meta.get("chunk_index", faiss_id)
        if chunk_text:
            chunks.append((chunk_index, chunk_text))

    chunks.sort(key=lambda x: x[0])
    return [text for _, text in chunks]


def validate_saksham_chapter(
    class_level: int, subject: str, chapter_ref: str
) -> dict[str, Any]:
    """Validate chapter exists in manifest and index."""
    chapter = get_chapter_from_manifest(class_level, subject, chapter_ref)
    if chapter is None:
        raise ValidationError(
            f"Chapter '{chapter_ref}' not found for class {class_level}, subject '{subject}'."
        )
    chunk_texts = get_chapter_chunk_texts(class_level, subject, chapter_ref)
    if not chunk_texts:
        raise ValidationError(
            f"No indexed content for chapter '{chapter_ref}'. Run ingest_curriculum.py --force."
        )
    return chapter
