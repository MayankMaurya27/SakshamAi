"""Unit tests for BM25 chapter store."""

from ai.bm25_store import ChapterBM25, SakshamBM25Store, tokenize


def test_tokenize_lowercase_words():
    tokens = tokenize("Minimum Wages for farm labourers")
    assert "minimum" in tokens
    assert "wages" in tokens
    assert "farm" in tokens


def test_chapter_bm25_ranks_relevant_chunk():
    docs = [
        "Land area under cultivation is practically fixed since 1960 in Palampur.",
        "The minimum wages for a farm labourer set by the government is Rs 300 per day, "
        "but Dala gets only Rs 160. There is heavy competition for work among farm labourers.",
        "Electricity came to Palampur and farmers use tubewells for irrigation.",
    ]
    bm25 = ChapterBM25([0, 1, 2], docs)
    hits = bm25.search("Why are wages for farm labourers less than minimum wages?", top_k=1)
    assert hits
    assert hits[0][0] == 1


def test_build_from_faiss_metadata_groups_by_chapter():
    id_map = {
        1: {
            "class": 9,
            "subject": "Economics",
            "chapter_id": "palampur",
            "chunk_text": "Chunk one about wages.",
        },
        2: {
            "class": 9,
            "subject": "Economics",
            "chapter_id": "palampur",
            "chunk_text": "Chunk two about electricity.",
        },
    }
    payload = SakshamBM25Store.build_from_faiss_metadata(id_map)
    assert payload["version"] == 1
    assert len(payload["chapters"]) == 1
    key = next(iter(payload["chapters"]))
    assert len(payload["chapters"][key]["documents"]) == 2
