"""RAG retrieval service for document and Saksham knowledge base."""

import logging
import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from ai.bm25_store import get_bm25_store
from ai.embeddings import embed_text
from ai.faiss_manager import get_saksham_index, get_user_index
from ai.hybrid_search import reciprocal_rank_fusion
from ai.reranker import get_reranker
from config.settings import get_settings
from database.repositories import ChunkRepository
from services.curriculum_utils import chapter_matches

logger = logging.getLogger(__name__)
settings = get_settings()

_CONTENT_REF_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bactivity\s*(\d+(?:\.\d+)?)", re.I), "Activity {ref}"),
    (re.compile(r"\bfig(?:ure)?\.?\s*(\d+(?:\.\d+)?)", re.I), "Fig. {ref}"),
    (re.compile(r"\bexercise\s*(\d+(?:\.\d+)?)", re.I), "Exercise {ref}"),
    (re.compile(r"\bsection\s*(\d+(?:\.\d+)?)", re.I), "{ref}"),
]


def extract_content_refs(question: str) -> list[str]:
    """Extract textbook activity/figure/section references from a question."""
    refs: list[str] = []
    seen: set[str] = set()
    for pattern, template in _CONTENT_REF_PATTERNS:
        for match in pattern.finditer(question):
            ref_num = match.group(1)
            for candidate in (template.format(ref=ref_num), ref_num):
                key = candidate.lower()
                if key not in seen:
                    seen.add(key)
                    refs.append(candidate)

    has_specific_ref = any(
        ref.lower().startswith(("activity", "fig", "exercise"))
        for ref in refs
    )
    if has_specific_ref:
        refs = [ref for ref in refs if not re.fullmatch(r"\d+(?:\.\d+)?", ref)]

    return refs


_QUERY_STOP_WORDS = frozenset(
    {
        "who",
        "what",
        "when",
        "where",
        "why",
        "how",
        "which",
        "was",
        "were",
        "is",
        "are",
        "the",
        "a",
        "an",
        "of",
        "in",
        "on",
        "at",
        "to",
        "for",
        "and",
        "or",
        "explain",
        "describe",
        "tell",
        "about",
        "from",
        "this",
        "that",
        "does",
        "do",
        "did",
    }
)

_PROFILE_HEADERS = (
    "be a scientist",
    "ever heard of",
    "our scientific heritage",
    "do you know",
)


def extract_query_terms(question: str) -> list[str]:
    """Extract proper names and key phrases from a student question."""
    terms: list[str] = []
    seen: set[str] = set()

    def add(term: str) -> None:
        cleaned = term.strip(" ?.,!\"'")
        cleaned = re.sub(r"^(?:the|a|an)\s+", "", cleaned, flags=re.I)
        if len(cleaned) < 3:
            return
        if cleaned.lower() in _QUERY_STOP_WORDS:
            return
        key = cleaned.lower()
        if key in seen:
            return
        seen.add(key)
        terms.append(cleaned)

    for match in re.finditer(
        r"\b(?:who|what)\s+(?:was|is|were|are)\s+(.+?)(?:\?|$)",
        question,
        re.I,
    ):
        add(match.group(1))

    for match in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", question):
        add(match.group(1))

    for match in re.finditer(r"\b([A-Z][a-z]{3,})\b", question):
        add(match.group(1))

    return terms


_CONTENT_EXTRA_STOP = frozenset(
    {
        "help",
        "helps",
        "helped",
        "many",
        "much",
        "more",
        "most",
        "some",
        "such",
        "also",
        "only",
        "just",
        "like",
        "very",
        "well",
        "come",
        "came",
        "make",
        "made",
        "take",
        "taken",
        "give",
        "given",
        "get",
        "got",
        "less",
        "greater",
        "become",
        "became",
    }
)


def _extract_content_phrases(question: str) -> list[str]:
    """Extract multi-word phrases from a question for focused chapter retrieval."""
    words = re.findall(r"[a-zA-Z']+", question.lower())
    content_words = [
        word
        for word in words
        if word not in _QUERY_STOP_WORDS
        and word not in _CONTENT_EXTRA_STOP
        and len(word) > 2
    ]

    phrases: list[str] = []
    seen: set[str] = set()
    for size in (3, 2):
        for index in range(len(content_words) - size + 1):
            phrase = " ".join(content_words[index : index + size])
            if phrase not in seen:
                seen.add(phrase)
                phrases.append(phrase)
    return phrases


def get_search_terms(question: str) -> list[str]:
    """Merge textbook references with named-entity and content phrases for retrieval."""
    content_refs = extract_content_refs(question)
    query_terms = extract_query_terms(question)
    phrases = _extract_content_phrases(question)
    ref_keys = {ref.lower() for ref in content_refs}
    merged = list(content_refs)
    for term in query_terms + phrases:
        if term.lower() not in ref_keys:
            merged.append(term)
            ref_keys.add(term.lower())
    return merged


def _is_low_quality_chunk(text: str) -> bool:
    """Filter page footers and near-empty chunks that pollute semantic search."""
    stripped = text.strip()
    if len(stripped) < 80:
        return True
    if stripped.count(".") / len(stripped) > 0.25:
        return True
    return False


_NEXT_ACTIVITY_PATTERN = re.compile(r"\bActivity\s+\d+(?:\.\d+)?", re.I)
_PASSAGE_STOP_PATTERN = re.compile(
    r"Let us now try to understand|Let us find out if the atmosphere|"
    r"Do liquids also exert pressure on the walls|"
    r"Ever heard of|Do you know that the base of a dam|"
    r"Gravitational force",
    re.I,
)


def _merge_chunk_text(previous: str, nxt: str) -> str:
    """Append the next chunk, removing duplicated overlap from PDF chunking."""
    max_overlap = min(len(previous), len(nxt), 800)
    for size in range(max_overlap, 30, -1):
        if previous[-size:] == nxt[:size]:
            return previous + nxt[size:]
    return f"{previous}\n{nxt}"


def _parse_activity_ref(activity_ref: str) -> tuple[int, int] | None:
    """Parse 'Activity 6.2' into (chapter, section) numbers."""
    match = re.search(r"Activity\s+(\d+)\.(\d+)", activity_ref, re.I)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def _find_passage_end(text: str, activity_ref: str) -> int:
    """Find where the current activity passage should end inside a text block."""
    current = _parse_activity_ref(activity_ref)
    end = len(text)

    for match in _NEXT_ACTIVITY_PATTERN.finditer(text):
        other = _parse_activity_ref(match.group())
        if other and other != current:
            end = min(end, match.start())

    stop = _PASSAGE_STOP_PATTERN.search(text)
    if stop:
        end = min(end, stop.start())

    return end


def _score_activity_header(text: str, start: int, activity_ref: str) -> float:
    """Prefer real activity headers over broken PDF fragment matches."""
    window = text[start : start + 300]
    aim_match = re.search(rf"{re.escape(activity_ref)}:\s*(.+)", window, re.I)
    if not aim_match:
        return 0.0

    score = 0.0
    aim = aim_match.group(1).strip()
    if aim.lower().startswith("let us"):
        score += 3.0
    if re.search(r"\s+z\s+", window) or " z Take" in window:
        score += 2.0
    if len(aim) > 10:
        score += 1.0
    if start > 0 and text[start - 1].isalnum():
        score -= 2.0
    return score


def _find_best_activity_start(
    ordered_chunks: list[tuple[int, str, int]],
    activity_ref: str,
) -> tuple[int, int] | None:
    """Return the chunk index and offset of the best activity header match."""
    ref_lower = activity_ref.lower()
    best: tuple[int, int] | None = None
    best_score = 0.0

    for index, (_, text, _) in enumerate(ordered_chunks):
        pos = 0
        while True:
            pos = text.lower().find(ref_lower, pos)
            if pos < 0:
                break
            score = _score_activity_header(text, pos, activity_ref)
            if score > best_score:
                best_score = score
                best = (index, pos)
            pos += len(ref_lower)

    return best if best_score >= 2.0 else None


def _get_ordered_chapter_chunks(
    saksham_index,
    chapter_filter,
) -> list[tuple[int, str, int]]:
    """Return (chunk_index, text, faiss_id) tuples sorted by chunk_index."""
    chunks: list[tuple[int, str, int]] = []
    for faiss_id, meta in saksham_index.id_map.items():
        if not chapter_filter(meta):
            continue
        text = meta.get("chunk_text", "")
        if not text or _is_low_quality_chunk(text):
            continue
        chunks.append((meta.get("chunk_index", faiss_id), text, faiss_id))
    chunks.sort(key=lambda item: item[0])
    return chunks


def _extract_activity_passage(
    ordered_chunks: list[tuple[int, str, int]],
    activity_ref: str,
) -> str | None:
    """Extract the full text of one activity across overlapping PDF chunks."""
    located = _find_best_activity_start(ordered_chunks, activity_ref)
    if located is None:
        return None

    start_idx, start_offset = located
    first_text = ordered_chunks[start_idx][1][start_offset:]
    first_end = _find_passage_end(first_text, activity_ref)
    parts = [first_text[:first_end]]

    if first_end < len(first_text):
        passage = "\n".join(parts).strip()
        return passage or None

    for _, text, _ in ordered_chunks[start_idx + 1 :]:
        end = _find_passage_end(text, activity_ref)
        segment = text[:end]
        parts[0] = _merge_chunk_text(parts[0], segment)
        if end < len(text):
            break

    passage = parts[0].strip()
    return passage or None


def _profile_start(text_lower: str, name_pos: int) -> int:
    """Pick the sidebar header closest before the person's name."""
    best = name_pos
    best_distance = float("inf")
    for header in _PROFILE_HEADERS:
        hpos = text_lower.rfind(header, max(0, name_pos - 700), name_pos + 40)
        if hpos < 0:
            continue
        distance = name_pos - hpos
        if distance < best_distance:
            best_distance = distance
            best = hpos
    return best


def _extract_profile_snippet(text: str, name_pos: int) -> str:
    """Extract a textbook sidebar profile around a person's name."""
    text_lower = text.lower()
    start = _profile_start(text_lower, name_pos)

    end = min(len(text), name_pos + 1600)
    for pattern in (
        re.compile(r"(?<=\.)\s+\d+\.\d+\s"),
        re.compile(r"\bActivity\s+\d", re.I),
        re.compile(r"Reprint\s+20", re.I),
    ):
        match = pattern.search(text, name_pos)
        if match and match.start() < end:
            end = match.start()

    return text[start:end].strip()


def _extract_focused_snippet(
    text: str,
    refs: list[str],
    before_chars: int = 200,
    after_chars: int = 2800,
) -> str:
    """Extract text around the strongest reference match inside one chunk."""
    text_lower = text.lower()
    best_pos = -1
    best_priority = -1.0
    best_ref = ""

    for ref in sorted(refs, key=len, reverse=True):
        pos = text_lower.find(ref.lower())
        if pos < 0:
            continue
        ref_lower = ref.lower()
        if ref_lower.startswith("activity"):
            priority = 3.0
        elif ref_lower.startswith("fig"):
            priority = 2.5
        elif ref_lower.startswith("exercise"):
            priority = 2.0
        elif " " in ref_lower:
            priority = 3.5
        else:
            priority = 1.5
        if priority > best_priority:
            best_priority = priority
            best_pos = pos
            best_ref = ref

    if best_pos < 0:
        return text

    if " " in best_ref.lower():
        return _extract_profile_snippet(text, best_pos)

    start = max(0, best_pos - before_chars)
    end = min(len(text), best_pos + after_chars)
    return text[start:end].strip()


@dataclass
class ChunkContext:
    """Retrieved chunk with metadata."""

    text: str
    score: float
    faiss_id: int
    metadata: dict


def _keyword_match_score(text: str, refs: list[str]) -> float:
    """Score how strongly a chunk matches explicit textbook references or phrases."""
    text_lower = text.lower()
    best = 0.0
    matched_phrases = 0
    for ref in sorted(refs, key=len, reverse=True):
        if ref.lower() not in text_lower:
            continue
        ref_lower = ref.lower()
        if ref_lower.startswith("activity"):
            best = max(best, 3.0)
        elif ref_lower.startswith("fig"):
            best = max(best, 2.5)
        elif ref_lower.startswith("exercise"):
            best = max(best, 2.0)
        elif " " in ref_lower:
            matched_phrases += 1
            best = max(best, 3.5 + min(matched_phrases - 1, 2) * 0.5)
        else:
            best = max(best, 1.5)
    return best


def _is_strong_keyword_match(score: float, search_terms: list[str], text: str) -> bool:
    """Return True when a keyword hit is specific enough to include in context."""
    if score >= 2.5:
        return True
    text_lower = text.lower()
    return any(" " in term and term.lower() in text_lower for term in search_terms)


def _prepend_phrase_matched_chunks(
    contexts: list[ChunkContext],
    candidates: list[tuple[int, str, int, dict]],
    search_terms: list[str],
    seen_keys: set[str],
    max_boost: int = 2,
) -> list[ChunkContext]:
    """Prepend chunks that contain the most specific question phrases."""
    phrase_terms = sorted(
        [term for term in search_terms if " " in term.strip()],
        key=len,
        reverse=True,
    )
    boosted: list[ChunkContext] = []

    for phrase in phrase_terms:
        if len(boosted) >= max_boost:
            break
        phrase_lower = phrase.lower()
        best: tuple[int, str, int, dict] | None = None

        for chunk_index, text, faiss_id, meta in candidates:
            if not text or phrase_lower not in text.lower():
                continue
            key = text[:200]
            if key in seen_keys:
                continue
            if best is None or chunk_index < best[0]:
                best = (chunk_index, text, faiss_id, meta)

        if best is None:
            continue

        chunk_index, text, faiss_id, meta = best
        key = text[:200]
        seen_keys.add(key)
        boosted.append(
            ChunkContext(
                text=text,
                score=4.0,
                faiss_id=faiss_id,
                metadata={
                    **meta,
                    "match_type": "phrase",
                    "phrase": phrase,
                    "chunk_index": chunk_index,
                },
            )
        )

    if not boosted:
        return contexts
    return boosted + contexts


def _merge_semantic_and_keyword_contexts(
    semantic_items: list[tuple[int, float, str, dict]],
    keyword_contexts: list[ChunkContext],
    search_terms: list[str],
    k: int,
    use_keyword_only: bool,
) -> list[ChunkContext]:
    """Prefer semantic matches, then add specific keyword hits without generic noise."""
    contexts: list[ChunkContext] = []
    seen_keys: set[str] = set()

    if use_keyword_only:
        for ctx in keyword_contexts:
            focused_text = _extract_focused_snippet(ctx.text, search_terms)
            key = focused_text[:200]
            if key in seen_keys:
                continue
            seen_keys.add(key)
            contexts.append(
                ChunkContext(
                    text=focused_text,
                    score=ctx.score,
                    faiss_id=ctx.faiss_id,
                    metadata=ctx.metadata,
                )
            )
            if len(contexts) >= k:
                break
        return contexts

    for faiss_id, score, text, meta in semantic_items:
        if len(contexts) >= k:
            break
        if not text or _is_low_quality_chunk(text):
            continue
        key = text[:200]
        if key in seen_keys:
            continue
        seen_keys.add(key)
        contexts.append(
            ChunkContext(
                text=text,
                score=score,
                faiss_id=faiss_id,
                metadata={**meta, "match_type": "semantic"},
            )
        )

    for ctx in keyword_contexts:
        if len(contexts) >= k:
            break
        if not _is_strong_keyword_match(ctx.score, search_terms, ctx.text):
            continue
        key = ctx.text[:200]
        if key in seen_keys:
            continue
        seen_keys.add(key)
        contexts.append(
            ChunkContext(
                text=ctx.text,
                score=ctx.score,
                faiss_id=ctx.faiss_id,
                metadata=ctx.metadata,
            )
        )

    return contexts


def _has_strong_keyword_match(contexts: list["ChunkContext"]) -> bool:
    """Return True when keyword matches are specific enough to skip semantic noise."""
    return any(ctx.score >= 3.0 for ctx in contexts)


def _should_use_keyword_only_retrieval(
    content_refs: list[str],
    question: str,
) -> bool:
    """
    Use keyword-only retrieval for activities, figures, or person biographies.

    General chapter questions (e.g. 'What was the French Revolution?') should use
    semantic search so the LLM gets a small relevant slice, not every mention of
  a phrase copied from the textbook.
    """
    if any(
        ref.lower().startswith(("activity", "fig", "exercise"))
        for ref in content_refs
    ):
        return True

    from ai.bio_formatter import is_bio_question

    return is_bio_question(question)


def _get_ordered_document_chunks(
    db: Session,
    document_id: int,
) -> list[tuple[int, str, int]]:
    """Return (chunk_index, text, faiss_id) for a uploaded document."""
    chunk_repo = ChunkRepository(db)
    records = chunk_repo.get_by_document_id(document_id)
    return [(c.chunk_index, c.chunk_text, c.faiss_id) for c in records]


def retrieve_document_context(
    question: str,
    db: Session,
    document_id: int | None = None,
    top_k: int | None = None,
) -> list[ChunkContext]:
    """Retrieve relevant chunks from user document index."""
    k = top_k or settings.top_k
    content_refs = extract_content_refs(question)
    search_terms = get_search_terms(question)
    chunk_repo = ChunkRepository(db)

    activity_refs = [ref for ref in content_refs if ref.lower().startswith("activity")]
    if activity_refs and document_id is not None:
        ordered_chunks = _get_ordered_document_chunks(db, document_id)
        passage = _extract_activity_passage(ordered_chunks, activity_refs[0])
        if passage:
            logger.info(
                "Using full activity passage for %s (document_id=%s)",
                activity_refs[0],
                document_id,
            )
            return [
                ChunkContext(
                    text=passage,
                    score=3.0,
                    faiss_id=ordered_chunks[0][2] if ordered_chunks else 0,
                    metadata={
                        "match_type": "activity_passage",
                        "activity": activity_refs[0],
                        "document_id": document_id,
                    },
                )
            ]

    query_vector = embed_text(question, is_query=True)
    user_index = get_user_index()
    results = user_index.search(query_vector, top_k=max(k * 2, k))

    if not results:
        logger.info("No results from user index for query")
        return []

    faiss_ids = [faiss_id for faiss_id, _, _ in results]
    chunks = chunk_repo.get_by_faiss_ids(faiss_ids)
    chunk_by_faiss = {chunk.faiss_id: chunk for chunk in chunks}

    keyword_contexts: list[ChunkContext] = []
    if search_terms and document_id is not None:
        for record in chunk_repo.get_by_document_id(document_id):
            text = record.chunk_text
            if not text or _is_low_quality_chunk(text):
                continue
            match_score = _keyword_match_score(text, search_terms)
            if match_score <= 0:
                continue
            keyword_contexts.append(
                ChunkContext(
                    text=text,
                    score=match_score,
                    faiss_id=record.faiss_id,
                    metadata={
                        "match_type": "keyword",
                        "chunk_index": record.chunk_index,
                        "document_id": document_id,
                    },
                )
            )
        keyword_contexts.sort(
            key=lambda ctx: (
                -ctx.score,
                ctx.metadata.get("chunk_index", ctx.faiss_id),
            )
        )

    contexts: list[ChunkContext] = []
    seen_keys: set[str] = set()
    use_keyword_only = _has_strong_keyword_match(
        keyword_contexts
    ) and _should_use_keyword_only_retrieval(content_refs, question)

    semantic_items: list[tuple[int, float, str, dict]] = []
    for faiss_id, score, meta in results:
        chunk = chunk_by_faiss.get(faiss_id)
        if chunk is None:
            continue
        if document_id is not None and chunk.document_id != document_id:
            continue
        text = chunk.chunk_text
        if _is_low_quality_chunk(text):
            continue
        semantic_items.append((faiss_id, score, text, meta))

    contexts = _merge_semantic_and_keyword_contexts(
        semantic_items,
        keyword_contexts,
        search_terms,
        k,
        use_keyword_only,
    )

    if use_keyword_only and contexts:
        logger.info(
            "Retrieved %d focused document chunks (keyword-only, document_id=%s)",
            len(contexts),
            document_id,
        )
        return contexts

    if search_terms and document_id is not None:
        candidates = [
            (
                record.chunk_index,
                record.chunk_text,
                record.faiss_id,
                {"match_type": "phrase", "document_id": document_id},
            )
            for record in chunk_repo.get_by_document_id(document_id)
            if record.chunk_text and not _is_low_quality_chunk(record.chunk_text)
        ]
        seen_keys = {ctx.text[:200] for ctx in contexts}
        contexts = _prepend_phrase_matched_chunks(
            contexts,
            candidates,
            search_terms,
            seen_keys,
        )[:k]

    logger.info("Retrieved %d document chunks (document_id=%s)", len(contexts), document_id)
    return contexts


def _get_chapter_chunk_texts(
    class_level: int, subject: str, chapter_ref: str
) -> list[str]:
    """Return ordered chunk texts for a chapter from FAISS metadata."""
    from services.knowledge_service import get_chapter_chunk_texts

    return get_chapter_chunk_texts(class_level, subject, chapter_ref)


def _augment_contexts_with_chapter_intro(
    contexts: list[ChunkContext],
    ordered_chunks: list[tuple[int, str, int]],
    intro_count: int = 2,
) -> list[ChunkContext]:
    """Prepend early chapter chunks so broad questions include causes and background."""
    if not ordered_chunks or intro_count <= 0:
        return contexts

    seen_keys = {ctx.text[:200] for ctx in contexts}
    intro_contexts: list[ChunkContext] = []

    for chunk_index, text, faiss_id in ordered_chunks[:intro_count]:
        if not text or _is_low_quality_chunk(text):
            continue
        key = text[:200]
        if key in seen_keys:
            continue
        seen_keys.add(key)
        intro_contexts.append(
            ChunkContext(
                text=text,
                score=2.5,
                faiss_id=faiss_id,
                metadata={
                    "match_type": "chapter_intro",
                    "chunk_index": chunk_index,
                },
            )
        )

    if not intro_contexts:
        return contexts

    return intro_contexts + contexts


def _resolve_chapter_id(
    class_level: int,
    subject: str,
    chapter_ref: str,
    chapter_filter,
    saksham_index,
) -> str:
    """Resolve stable chapter_id for BM25 lookup."""
    from services.knowledge_service import get_chapter_from_manifest

    chapter = get_chapter_from_manifest(class_level, subject, chapter_ref)
    if chapter and chapter.get("chapter_id"):
        return str(chapter["chapter_id"])

    for _, meta in saksham_index.id_map.items():
        if chapter_filter(meta) and meta.get("chapter_id"):
            return str(meta["chapter_id"])
    return chapter_ref.strip().lower().replace(" ", "_")


def _hybrid_retrieve_chapter(
    question: str,
    class_level: int,
    subject: str,
    chapter_ref: str,
    chapter_filter,
    saksham_index,
    search_terms: list[str],
    k: int,
) -> list[ChunkContext]:
    """
    Hybrid retrieval: semantic + BM25 + RRF + optional reranker.

    Designed for offline Jetson deployment with pre-built indexes.
    """
    candidate_k = max(settings.retrieval_candidate_count, k * 2)
    chapter_id = _resolve_chapter_id(
        class_level, subject, chapter_ref, chapter_filter, saksham_index
    )

    query_vector = embed_text(question, is_query=True)
    semantic_results = saksham_index.search_filtered(
        query_vector, chapter_filter, top_k=candidate_k
    )
    semantic_ranked = [faiss_id for faiss_id, _, _ in semantic_results]

    ranked_lists = [semantic_ranked]
    if settings.bm25_enabled:
        bm25_hits = get_bm25_store().search_chapter(
            class_level,
            subject,
            chapter_id,
            question,
            top_k=candidate_k,
        )
        if bm25_hits:
            ranked_lists.append([faiss_id for faiss_id, _, _ in bm25_hits])
        elif settings.saksham_bm25_index_path.exists() is False:
            logger.debug("BM25 sidecar missing; using semantic retrieval only")

    fused = reciprocal_rank_fusion(ranked_lists, k=settings.rrf_k)
    fused_ids = [faiss_id for faiss_id, _ in fused]

    if search_terms:
        candidates: list[tuple[int, str, int, dict]] = []
        for faiss_id, meta in saksham_index.id_map.items():
            if not chapter_filter(meta):
                continue
            text = meta.get("chunk_text", "")
            if not text or _is_low_quality_chunk(text):
                continue
            candidates.append(
                (
                    meta.get("chunk_index", faiss_id),
                    text,
                    faiss_id,
                    meta,
                )
            )
        seen_ids = set(fused_ids)
        phrase_contexts = _prepend_phrase_matched_chunks(
            [],
            candidates,
            search_terms,
            set(),
            max_boost=2,
        )
        for ctx in phrase_contexts:
            if ctx.faiss_id not in seen_ids:
                fused_ids.insert(0, ctx.faiss_id)
                seen_ids.add(ctx.faiss_id)

    rerank_candidates: list[tuple[int, str]] = []
    for faiss_id in fused_ids[:candidate_k]:
        meta = saksham_index.id_map.get(faiss_id, {})
        text = meta.get("chunk_text", "")
        if not text or _is_low_quality_chunk(text):
            continue
        rerank_candidates.append((faiss_id, text))

    if settings.rerank_enabled and len(rerank_candidates) > k:
        reranked = get_reranker().rerank(question, rerank_candidates, top_k=k)
    else:
        reranked = [
            (faiss_id, 1.0, text)
            for faiss_id, text in rerank_candidates[:k]
        ]

    contexts: list[ChunkContext] = []
    for faiss_id, score, text in reranked:
        meta = saksham_index.id_map.get(faiss_id, {})
        contexts.append(
            ChunkContext(
                text=text,
                score=score,
                faiss_id=faiss_id,
                metadata={**meta, "match_type": "hybrid"},
            )
        )

    logger.info(
        "Hybrid retrieval: %d results (semantic=%d, bm25=%s, rerank=%s, chapter=%s)",
        len(contexts),
        len(semantic_ranked),
        len(ranked_lists) > 1,
        settings.rerank_enabled,
        chapter_id,
    )
    return contexts


def retrieve_saksham_context(
    question: str,
    class_level: int,
    subject: str,
    chapter_ref: str,
    top_k: int | None = None,
) -> list[ChunkContext]:
    """
    Retrieve relevant chunks for a Saksham curriculum chapter.

    Uses chapter-scoped FAISS search first, then falls back to all chapter chunks
    in document order if semantic search returns nothing.
    """
    k = top_k or settings.top_k
    saksham_index = get_saksham_index()
    content_refs = extract_content_refs(question)
    search_terms = get_search_terms(question)

    def chapter_filter(meta: dict) -> bool:
        return chapter_matches(meta, class_level, subject, chapter_ref)

    activity_refs = [ref for ref in content_refs if ref.lower().startswith("activity")]
    if activity_refs:
        ordered_chunks = _get_ordered_chapter_chunks(saksham_index, chapter_filter)
        passage = _extract_activity_passage(ordered_chunks, activity_refs[0])
        if passage:
            logger.info(
                "Using full activity passage for %s (class=%s, chapter=%s)",
                activity_refs[0],
                class_level,
                chapter_ref,
            )
            return [
                ChunkContext(
                    text=passage,
                    score=3.0,
                    faiss_id=ordered_chunks[0][2] if ordered_chunks else 0,
                    metadata={
                        "match_type": "activity_passage",
                        "activity": activity_refs[0],
                    },
                )
            ]

    keyword_contexts: list[ChunkContext] = []
    if search_terms:
        for faiss_id, meta in saksham_index.id_map.items():
            if not chapter_filter(meta):
                continue
            text = meta.get("chunk_text", "")
            if not text or _is_low_quality_chunk(text):
                continue
            match_score = _keyword_match_score(text, search_terms)
            if match_score <= 0:
                continue
            keyword_contexts.append(
                ChunkContext(
                    text=text,
                    score=match_score,
                    faiss_id=faiss_id,
                    metadata={**meta, "match_type": "keyword"},
                )
            )
        keyword_contexts.sort(
            key=lambda ctx: (
                -ctx.score,
                ctx.metadata.get("chunk_index", ctx.faiss_id),
            )
        )

    query_vector = embed_text(question, is_query=True)
    results = saksham_index.search_filtered(
        query_vector, chapter_filter, top_k=max(k * 2, k)
    )

    use_keyword_only = _has_strong_keyword_match(
        keyword_contexts
    ) and _should_use_keyword_only_retrieval(content_refs, question)

    if (
        settings.hybrid_retrieval_enabled
        and not use_keyword_only
        and not activity_refs
    ):
        contexts = _hybrid_retrieve_chapter(
            question,
            class_level,
            subject,
            chapter_ref,
            chapter_filter,
            saksham_index,
            search_terms,
            k,
        )
        if contexts:
            return contexts

    semantic_items: list[tuple[int, float, str, dict]] = []
    for faiss_id, score, meta in results:
        text = meta.get("chunk_text", "")
        if not text or _is_low_quality_chunk(text):
            continue
        semantic_items.append((faiss_id, score, text, meta))

    contexts = _merge_semantic_and_keyword_contexts(
        semantic_items,
        keyword_contexts,
        search_terms,
        k,
        use_keyword_only,
    )

    if use_keyword_only and contexts:
        logger.info(
            "Retrieved %d focused saksham chunks (keyword-only, class=%s, chapter=%s)",
            len(contexts),
            class_level,
            chapter_ref,
        )
        return contexts

    if search_terms:
        candidates: list[tuple[int, str, int, dict]] = []
        for faiss_id, meta in saksham_index.id_map.items():
            if not chapter_filter(meta):
                continue
            text = meta.get("chunk_text", "")
            if not text or _is_low_quality_chunk(text):
                continue
            candidates.append(
                (
                    meta.get("chunk_index", faiss_id),
                    text,
                    faiss_id,
                    meta,
                )
            )
        seen_keys = {ctx.text[:200] for ctx in contexts}
        contexts = _prepend_phrase_matched_chunks(
            contexts,
            candidates,
            search_terms,
            seen_keys,
        )[:k]

    if contexts:
        logger.info(
            "Retrieved %d saksham chunks (%d keyword, class=%s, chapter=%s)",
            len(contexts),
            sum(1 for c in contexts if c.metadata.get("match_type") == "keyword"),
            class_level,
            chapter_ref,
        )
        return contexts

    # Direct fallback: all chunks for this chapter in order
    chunk_texts = _get_chapter_chunk_texts(class_level, subject, chapter_ref)
    if chunk_texts:
        logger.info(
            "Using direct chapter fallback with %d chunks (class=%s, chapter=%s)",
            len(chunk_texts),
            class_level,
            chapter_ref,
        )
        return [
            ChunkContext(
                text=text,
                score=1.0,
                faiss_id=idx,
                metadata={"chunk_index": idx, "fallback": True},
            )
            for idx, text in enumerate(chunk_texts[:k])
        ]

    logger.info(
        "No saksham content for class=%s subject=%s chapter=%s",
        class_level,
        subject,
        chapter_ref,
    )
    return []
