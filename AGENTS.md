# Saksham AI — Instructions for AI Coding Agents

This file is read by GitHub Copilot, Antigravity, Codex, Claude Code, and similar tools.

## Project

**Saksham AI** — RAG backend for NCERT/CBSE (Classes 6–10) + user document uploads.  
Stack: FastAPI, FAISS, BM25, Ollama (`llama3.2:1b`), SQLite.

## Read before coding

| Priority | Document |
|----------|----------|
| 1 | `graphify-out/PROJECT_CONTEXT.md` — handoff, recent changes, conventions |
| 2 | `backend/ARCHITECTURE.md` — RAG ingest, retrieval, `/ask` |
| 3 | `graphify-out/wiki/index.md` — topic index |
| 4 | `graphify-out/GRAPH_REPORT.md` — dependency graph audit |

## Navigate with graphify (required when graph exists)

If `graphify-out/graph.json` exists:

```bash
graphify query "<architecture question>"
graphify path "<symbol A>" "<symbol B>"
graphify explain "<concept>"
```

Use Read/Grep only **after** graphify orients you, or when `graph.json` is missing.

After code changes: `graphify update backend`

## Recent important changes (quiz, 2026-06)

- Generic **grounded quiz pipeline** in `services/quiz_grounded.py` (not per-chapter templates)
- Quality gates: verify against source text, ban filler options, tier order definitions → lists → LLM → cloze
- **Fixed** `get_chapter_from_manifest()` wrong chapter bug (Electricity → Acids)
- Cache version: `QUIZ_CACHE_VERSION=v11-quality-gate`
- Tests: `tests/unit/test_quiz_*.py`, `tests/api/test_quiz_api.py`

Details: `graphify-out/wiki/quiz-generation.md`

## Conventions

- Minimize scope; no one-off chapter patches for quiz
- Match existing module style
- Bump `quiz_cache_version` when quiz output/validation changes
- Never commit `.env` secrets
- Run quiz tests after quiz edits

## Local dev

```bash
cd backend && source .venv/bin/activate
uvicorn app:app --reload --port 8000
```

## Key paths

```
backend/api/           REST endpoints
backend/services/      RAG, quiz, knowledge
backend/ai/            retrieval, LLM, prompts
backend/data/saksham_kb/   curriculum PDFs + manifest.json
backend/data/faiss/        indexes (large)
graphify-out/          knowledge graph + agent wiki
```
