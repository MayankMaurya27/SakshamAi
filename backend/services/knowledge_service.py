"""Saksham educational knowledge base and curriculum indexing."""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

from ai.bm25_store import SakshamBM25Store
from ai.faiss_manager import FaissManager, get_saksham_index, reset_saksham_index, save_saksham_index
import ai.faiss_manager as faiss_manager_module
from config.settings import get_settings
from documents.chunker import create_curriculum_chunks
from documents.indexer import index_document
from documents.pdf_parser import extract_text
from exceptions import ValidationError
from services.curriculum_utils import (
    ChapterInfo,
    chapter_matches,
    discover_chapter_pdfs,
    resolve_chapter_ref,
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
    """Hash curriculum PDFs and index version for staleness detection."""
    hasher = hashlib.sha256()
    hasher.update(settings.saksham_index_version.encode("utf-8"))
    kb_dir = settings.saksham_kb_dir
    if not kb_dir.exists():
        return hasher.hexdigest()

    for pdf_file in sorted(kb_dir.rglob("*.pdf")):
        hasher.update(pdf_file.read_bytes())

    return hasher.hexdigest()


def ingest_chapter_pdf(chapter: ChapterInfo, saksham_index) -> dict[str, Any]:
    """Extract, chunk, and index a single chapter PDF."""
    text, page_count = extract_text(str(chapter.pdf_path))
    chunks = create_curriculum_chunks(text)
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


def _chapter_key(
    class_level: int | None,
    subject: str | None,
    chapter_id: str | None,
) -> tuple[int, str, str] | None:
    """Normalize chapter identity for manifest and index lookups."""
    if class_level is None or not subject or not chapter_id:
        return None
    return (class_level, subject.lower(), chapter_id.lower())


def _discovered_chapter_keys(chapters: list[ChapterInfo]) -> set[tuple[int, str, str]]:
    """Return identity keys for all PDFs discovered on disk."""
    keys: set[tuple[int, str, str]] = set()
    for chapter in chapters:
        key = _chapter_key(chapter.class_level, chapter.subject, chapter.chapter_id)
        if key:
            keys.add(key)
    return keys


def _is_deployable_without_pdf(chapter: dict[str, Any]) -> bool:
    """
    Return True for chapters intentionally shipped without source PDFs.

    Only Class 8 Science uses pre-built index content with PDFs removed at deploy
    time. Other subjects should re-index when PDFs are renamed or replaced.
    """
    return (
        chapter.get("class") == 8
        and chapter.get("subject", "").lower() == "science"
        and not chapter.get("legacy_json")
    )


def _preserve_chapters_without_pdfs(
    old_index: FaissManager,
    discovered_keys: set[tuple[int, str, str]],
    old_manifest: dict[str, Any],
) -> list[tuple[np.ndarray, dict[str, Any]]]:
    """
    Export indexed vectors for deployable chapters whose PDFs are no longer on disk.

    This keeps pre-built Class 8 Science content available after PDFs are removed
    for deployment, without retaining stale entries when PDFs are renamed elsewhere.
    """
    if old_index.index is None or old_index.total_vectors == 0:
        return []

    preserve_keys = {
        key
        for chapter in old_manifest.get("chapters", [])
        if (key := _chapter_key(
            chapter.get("class"),
            chapter.get("subject"),
            chapter.get("chapter_id"),
        ))
        and key not in discovered_keys
        and _is_deployable_without_pdf(chapter)
    }

    preserved: list[tuple[np.ndarray, dict[str, Any]]] = []
    for faiss_id, meta in old_index.id_map.items():
        key = _chapter_key(meta.get("class"), meta.get("subject"), meta.get("chapter_id"))
        if key is None or key not in preserve_keys:
            continue
        vector = old_index.index.reconstruct(faiss_id)
        preserved.append((np.asarray(vector, dtype=np.float32), dict(meta)))

    return preserved


def _restore_preserved_vectors(
    saksham_index: FaissManager,
    preserved: list[tuple[np.ndarray, dict[str, Any]]],
) -> int:
    """Add preserved chapter vectors back into a freshly built index."""
    if not preserved:
        return 0

    vectors = np.vstack([vector.reshape(1, -1) for vector, _ in preserved])
    metadata = [meta for _, meta in preserved]
    saksham_index.add_vectors(vectors, metadata)
    return len(preserved)


def _preserved_manifest_entries(
    old_manifest: dict[str, Any],
    discovered_keys: set[tuple[int, str, str]],
) -> list[dict[str, Any]]:
    """Keep manifest rows for deployable chapters indexed without source PDFs."""
    entries: list[dict[str, Any]] = []
    for chapter in old_manifest.get("chapters", []):
        key = _chapter_key(
            chapter.get("class"),
            chapter.get("subject"),
            chapter.get("chapter_id"),
        )
        if (
            key
            and key not in discovered_keys
            and _is_deployable_without_pdf(chapter)
        ):
            entries.append(chapter)
    return entries


def _stored_curriculum_hash() -> str:
    """Read the last indexed curriculum hash, if present."""
    hash_path = settings.saksham_kb_hash_path
    if not hash_path.exists():
        return ""
    return hash_path.read_text(encoding="utf-8").strip()


def _prebuilt_index_available() -> bool:
    """Return True if a pre-built Saksham index and manifest exist on disk."""
    return (
        settings.saksham_index_path.exists()
        and settings.saksham_index_meta_path.exists()
        and manifest_path().exists()
    )


def _save_bm25_sidecar(saksham_index: FaissManager) -> None:
    """Build and persist BM25 sidecar from the FAISS metadata map."""
    if not settings.bm25_enabled:
        return

    payload = SakshamBM25Store.build_from_faiss_metadata(saksham_index.id_map)
    store = SakshamBM25Store()
    store.save(payload)
    logger.info(
        "Built BM25 sidecar with %d chapters at %s",
        len(payload.get("chapters", {})),
        settings.saksham_bm25_index_path,
    )


def build_saksham_index(force: bool = False) -> None:
    """
    Build or rebuild saksham FAISS index from curriculum PDFs.

    At runtime, if a pre-built index already exists and curriculum PDFs are unchanged,
    it is loaded and PDFs are not required (suitable for Jetson deployment).

    Rebuild when --force is used, when no pre-built index exists, or when new PDFs
    are added. Chapters already indexed but whose PDFs were removed are preserved.
    """
    current_hash = compute_curriculum_hash()
    stored_hash = _stored_curriculum_hash()
    hash_path = settings.saksham_kb_hash_path

    if (
        not force
        and _prebuilt_index_available()
        and current_hash
        and current_hash == stored_hash
    ):
        get_saksham_index()
        logger.info(
            "Using pre-built Saksham index (%d vectors); PDFs not required at runtime",
            get_saksham_index().total_vectors,
        )
        return

    chapters = discover_chapter_pdfs(settings.saksham_kb_dir)
    discovered_keys = _discovered_chapter_keys(chapters)

    old_index = get_saksham_index() if _prebuilt_index_available() else None
    old_manifest = load_manifest() if manifest_path().exists() else {"chapters": []}
    preserved_vectors = (
        _preserve_chapters_without_pdfs(old_index, discovered_keys, old_manifest)
        if old_index is not None
        else []
    )

    if not chapters and not preserved_vectors:
        logger.warning("No curriculum PDFs or preserved chapters to index")
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

    preserved_manifest = _preserved_manifest_entries(old_manifest, discovered_keys)
    if preserved_manifest:
        restored = _restore_preserved_vectors(saksham_index, preserved_vectors)
        manifest_entries.extend(preserved_manifest)
        total_chunks += restored
        logger.info(
            "Preserved %d chapters (%d vectors) without source PDFs",
            len(preserved_manifest),
            restored,
        )

    save_saksham_index()
    _save_bm25_sidecar(saksham_index)
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
    chapter_ref = resolve_chapter_ref(class_level, subject, chapter_ref)
    ref = chapter_ref.strip().lower()
    ref_slug = slugify(chapter_ref)
    for chapter in _manifest_chapters():
        if chapter.get("class") != class_level:
            continue
        if chapter.get("subject", "").lower() != subject.lower():
            continue
        chapter_id = chapter.get("chapter_id", "").lower()
        chapter_title = chapter.get("chapter_title", "").lower()
        if ref in {chapter_id, chapter_title}:
            return chapter
        if ref_slug == chapter_id or ref_slug == slugify(chapter.get("chapter_title", "")):
            return chapter
    return None


def get_chapter_chunk_texts(
    class_level: int, subject: str, chapter_ref: str
) -> list[str]:
    """Return all chunk texts for a chapter from FAISS metadata (direct lookup)."""
    chapter_ref = resolve_chapter_ref(class_level, subject, chapter_ref)
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
