"""Unit tests for optional cross-encoder reranker."""

from ai.reranker import CrossEncoderReranker, NoOpReranker


def test_noop_reranker_passthrough():
    candidates = [(1, "first chunk"), (2, "second chunk")]
    results = NoOpReranker().rerank("query", candidates, top_k=1)
    assert results == [(1, 1.0, "first chunk")]


def test_cross_encoder_falls_back_when_model_unavailable(monkeypatch):
    reranker = CrossEncoderReranker(
        model_name="missing-model",
        local_files_only=True,
    )
    monkeypatch.setattr(reranker, "_load_model", lambda: None)

    candidates = [(10, "wages chunk"), (11, "land chunk")]
    results = reranker.rerank("minimum wages", candidates, top_k=2)
    assert results == [(10, 1.0, "wages chunk"), (11, 1.0, "land chunk")]
