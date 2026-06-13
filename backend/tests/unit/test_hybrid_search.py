"""Unit tests for hybrid RRF merging."""

from ai.hybrid_search import reciprocal_rank_fusion


def test_reciprocal_rank_fusion_prefers_shared_hits():
    semantic = [10, 20, 30]
    bm25 = [20, 10, 40]
    fused = reciprocal_rank_fusion([semantic, bm25], k=60)
    top_ids = [faiss_id for faiss_id, _ in fused[:3]]
    assert 10 in top_ids
    assert 20 in top_ids
