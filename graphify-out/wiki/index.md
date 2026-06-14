# Saksham AI — Agent Wiki

Start here when exploring or modifying this codebase. This wiki complements the machine-readable graph in `graphify-out/graph.json`.

## Read first

1. **[Project context (handoff)](../PROJECT_CONTEXT.md)** — purpose, layout, recent quiz work, conventions
2. **[Backend architecture](../../backend/ARCHITECTURE.md)** — RAG ingest, hybrid retrieval, `/ask` pipeline
3. **[Graph report](../GRAPH_REPORT.md)** — dependency graph audit (god nodes, communities)

## Topic articles

| Article | Contents |
|---------|----------|
| [Quiz generation](quiz-generation.md) | Grounded MCQ pipeline, quality gates, cache, tests |
| [Retrieval & RAG](retrieval-rag.md) | FAISS, BM25, hybrid search, retriever |
| [API surface](api-endpoints.md) | FastAPI routes and request shapes |
| [Graphify usage](graphify-usage.md) | Query the graph; keep it updated |

## Navigate by question

| Question | Command / file |
|----------|------------------|
| What calls `generate_saksham_quiz`? | `graphify explain "generate_saksham_quiz"` |
| Path from quiz API to FAISS? | `graphify path "create_quiz" "FaissManager"` |
| How does `/ask` work end-to-end? | `graphify query "How does answer_question retrieve context?"` |
| What changed in quiz recently? | [quiz-generation.md](quiz-generation.md) |

## After you edit code

```bash
graphify update backend
cd backend && .venv/bin/pytest tests/unit/test_quiz_grounded.py tests/api/test_quiz_api.py -q
```

If quiz behavior changed, bump `QUIZ_CACHE_VERSION` in `backend/config/settings.py`.
