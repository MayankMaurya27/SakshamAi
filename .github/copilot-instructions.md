# Saksham AI — Copilot Instructions

Read **`AGENTS.md`** (repo root) and **`graphify-out/PROJECT_CONTEXT.md`** before suggesting or applying changes.

## Project

RAG backend for NCERT/CBSE curriculum. FastAPI + FAISS + BM25 + Ollama.

## Navigation

- Architecture: `backend/ARCHITECTURE.md`
- Knowledge graph: `graphify-out/graph.json` — use `graphify query "…"` when available
- Recent quiz work: `graphify-out/wiki/quiz-generation.md`

## Rules

1. Do not add per-chapter quiz templates; use `services/quiz_grounded.py`
2. After quiz changes, bump `QUIZ_CACHE_VERSION` and run quiz tests
3. Chapter lookup: `get_chapter_from_manifest()` — never match slug against all chapters
4. Minimize diff scope; match existing code style

## Tests

```bash
cd backend && .venv/bin/pytest tests/unit/test_quiz_grounded.py tests/api/test_quiz_api.py -q
```
