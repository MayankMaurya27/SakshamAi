"""Hybrid retrieval utilities: reciprocal rank fusion and candidate merging."""

from __future__ import annotations


def reciprocal_rank_fusion(
    ranked_id_lists: list[list[int]],
    k: int = 60,
) -> list[tuple[int, float]]:
    """
    Merge multiple ranked faiss_id lists using Reciprocal Rank Fusion.

    Returns faiss_ids sorted by fused score (highest first).
    """
    scores: dict[int, float] = {}

    for ranked_ids in ranked_id_lists:
        for rank, faiss_id in enumerate(ranked_ids, start=1):
            scores[faiss_id] = scores.get(faiss_id, 0.0) + 1.0 / (k + rank)

    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def merge_ranked_lists(
    primary: list[int],
    secondary: list[int],
    limit: int,
) -> list[int]:
    """Interleave two ranked lists without duplicates up to limit."""
    seen: set[int] = set()
    merged: list[int] = []

    max_len = max(len(primary), len(secondary))
    for i in range(max_len):
        for source in (primary, secondary):
            if i < len(source):
                faiss_id = source[i]
                if faiss_id not in seen:
                    seen.add(faiss_id)
                    merged.append(faiss_id)
                    if len(merged) >= limit:
                        return merged
    return merged
