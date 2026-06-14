# Retrieval & RAG

**Canonical doc:** `backend/ARCHITECTURE.md`

## Summary

Saksham answers curriculum questions by retrieving chunk text from a pre-built index, not from LLM memory.

### Ingest (one-time)

```
PDFs → pdf_parser → section chunker → embeddings (multilingual-e5-small)
  → FAISS index + saksham_index_meta.json + BM25 sidecar
```

**Scripts:** `scripts/ingest_curriculum.py --force`, startup via `build_saksham_index()` in `app.py`

### Runtime `/ask`

```
rag_service.answer_question()
  → question_router (STRICT vs GUIDED)
  → retriever (hybrid: FAISS + BM25 + RRF + optional rerank)
  → context_cleaner → prompt_builder → Ollama
  → answer_formatter
```

## Key modules

| Module | Role |
|--------|------|
| `ai/retriever.py` | Main retrieval orchestration |
| `ai/hybrid_search.py` | Reciprocal rank fusion |
| `ai/bm25_store.py` | Per-chapter BM25 |
| `ai/reranker.py` | Cross-encoder (optional) |
| `ai/embeddings.py` | e5-small vectors |
| `ai/faiss_manager.py` | Index load/search |
| `services/knowledge_service.py` | Manifest, chapter chunks |

## Settings

```env
BM25_ENABLED=true
HYBRID_RETRIEVAL_ENABLED=true
RERANK_ENABLED=true
TOP_K=5
RETRIEVAL_CANDIDATE_COUNT=20
saksham_index_version=v2-section-hybrid
```

## Graph entry points

```bash
graphify explain "answer_question"
graphify path "answer_question" "FaissManager"
graphify query "How does hybrid retrieval combine BM25 and FAISS?"
```

## Known limitations

- Exercise-list chunks can rank high for some queries
- `llama3.2:1b` produces short answers for explain-style questions
- See `ARCHITECTURE.md` § Known limitations
