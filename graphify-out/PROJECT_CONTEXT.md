# Saksham AI — Project Context (Agent Handoff)

**Last updated:** 2026-06-13  
**Scope:** Full repo; backend graph built from `backend/` (AST extraction, 1126 nodes)  
**Audience:** Any AI coding agent (Cursor, GitHub Copilot, Antigravity, Codex, Claude Code, etc.)

Read this file **before** making changes. Use `graphify query` / `path` / `explain` for dependency questions (see [How to navigate](#how-to-navigate-this-repo)).

---

## What Saksham AI is

Saksham AI is a **Retrieval-Augmented Generation (RAG)** backend for NCERT/CBSE curriculum (Classes 6–10) plus user-uploaded documents.

| Phase | What happens |
|-------|----------------|
| **Ingest (once)** | PDFs → text → section-aware chunks → embeddings → FAISS + BM25 indexes |
| **Runtime** | Question → hybrid retrieval → prompt → Ollama LLM → answer |

The LLM does **not** memorize the curriculum. It only sees **retrieved chunk text** in the prompt.

**Detailed architecture:** `backend/ARCHITECTURE.md` (canonical, kept in sync with code).

---

## Repository layout

```
SakshamAi/
├── backend/                 FastAPI app (main codebase)
│   ├── api/                 REST endpoints (/ask, /quiz, /upload, …)
│   ├── ai/                  Retrieval, LLM, prompts, formatters
│   ├── services/            RAG, quiz, knowledge, curriculum
│   ├── documents/           PDF parse, chunk, index
│   ├── database/            SQLite models + repositories
│   ├── config/settings.py   All env-driven settings
│   ├── data/
│   │   ├── saksham_kb/      NCERT PDFs + manifest.json
│   │   └── faiss/           Pre-built indexes (large JSON sidecars)
│   ├── scripts/             ingest_curriculum, download_models, seed_kb
│   └── tests/               unit + integration
├── graphify-out/            Knowledge graph + this handoff doc (YOU ARE HERE)
│   ├── graph.json           Queryable dependency graph
│   ├── GRAPH_REPORT.md      Auto-generated graph audit
│   ├── graph.html           Interactive visualization
│   └── wiki/                Topic articles for agents
└── AGENTS.md                Short entry point for all AI tools
```

---

## Core runtime flows

### POST /ask (RAG Q&A)

```
api/ask.py → services/rag_service.py → ai/retriever.py
  → hybrid_search (FAISS + BM25 + RRF) → optional reranker
  → ai/context_cleaner.py → ai/prompt_builder.py → ai/llm.py (Ollama)
```

**Sources:** `saksham` (curriculum) or `document` (user upload).  
**Key settings:** `BM25_ENABLED`, `HYBRID_RETRIEVAL_ENABLED`, `RERANK_ENABLED`, `TOP_K`, `OLLAMA_MODEL`.

### POST /quiz (MCQ generation)

```
api/quiz.py → services/quiz_service.py
  → Math: services/quiz_math.py (fact/template pipeline)
  → All other subjects: services/quiz_grounded.py (generic extractors)
  → LLM fallback (Ollama, batch size 1) when grounded count < requested
  → services/quiz_cache.py (file cache, versioned)
```

**Request example (Saksham chapter):**

```json
{
  "source": "saksham",
  "class_level": 10,
  "subject": "Science",
  "chapter": "Electricity",
  "question_count": 7
}
```

---

## Recent work: Quiz generation overhaul (2026-06)

**Problem:** `POST /quiz` often returned 422 (`minimum 5 questions`) or low-quality MCQs (OCR junk, `Option 1/2/3` fillers, wrong chapter metadata).

**Solution:** Generic **grounded + quality-gate** pipeline — not per-chapter templates.

### Pipeline (non-Math subjects)

```
Chapter chunks → filter_quiz_source_chunks
  → build_grounded (definitions → list items → cloze last)
  → verify_grounded_question (corpus + source_text)
  → if short: LLM (1 Q/call) → tag_llm_questions → verify_llm_question
  → strip_quiz_metadata → validate_question_batch (min 5) → cache → JSON
```

Math bypasses this and uses `quiz_math.py`.

### Key files

| File | Role |
|------|------|
| `services/quiz_grounded.py` | Generic extractors + verification (`verify_grounded_question`, `verify_llm_question`) |
| `services/quiz_service.py` | Orchestration, cache validation, LLM retry/merge |
| `services/quiz_science.py` | Thin wrapper → `quiz_grounded.py` (no hardcoded chapter templates) |
| `services/quiz_math.py` | Math-specific pipeline (unchanged pattern) |
| `services/quiz_cache.py` | File cache keyed by `chapter_id` + cache version |
| `services/knowledge_service.py` | Chapter lookup + chunk texts |
| `ai/prompt_builder.py` | Plain-text quiz prompt format |
| `ai/llm.py` | Ollama + MockLLM (tests use substantive options) |

### Quality gates

- **`_quiz_meta`** on internal questions: `source_type` = `definition` \| `list` \| `cloze` \| `llm`
- **`strip_quiz_metadata()`** before API/cache output
- **Banned:** filler distractors (`Option 1/2/3`), OCR garbage (`V V1 V2`), broken clozes
- **Definition distractors:** other chapter definition terms + list items (not random phrase fragments)
- **List distractors:** only other list items from same chunk
- **Tier order:** definitions → lists → **LLM** → cloze (last resort)
- **Cache invalidation:** ignore cache if `chapter_id`, `class_level`, or `subject` mismatch

### Bug fix: wrong chapter metadata

`get_chapter_from_manifest()` incorrectly included `slugify(chapter_ref)` in every chapter’s match set, so `"Electricity"` matched the **first** Class 10 Science chapter (`Acids, Bases and Salts`).

**Fix:** Compare `ref` / `ref_slug` only against each chapter’s own `chapter_id` and `chapter_title` (same logic as `chapter_matches()` in `curriculum_utils.py`).

### Settings (`.env` / `config/settings.py`)

```env
QUIZ_MIN_QUESTIONS=5
QUIZ_MAX_QUESTIONS=15
QUIZ_LLM_MAX_ATTEMPTS=5
QUIZ_LLM_BATCH_SIZE=1
QUIZ_CACHE_VERSION=v11-quality-gate
OLLAMA_MODEL=llama3.2:1b
OLLAMA_NUM_PREDICT_QUIZ=2048
```

After changing quiz logic: bump `QUIZ_CACHE_VERSION` or clear `backend/data/quiz_cache/*`.

### Tests (all passing)

```bash
cd backend
.venv/bin/pytest tests/unit/test_quiz_grounded.py \
  tests/unit/test_quiz_service.py tests/unit/test_quiz_science.py \
  tests/api/test_quiz_api.py -q
```

Also: `tests/unit/test_curriculum_utils.py` (chapter manifest lookup).

---

## Data & indexes

| Asset | Path | Notes |
|-------|------|-------|
| PDFs | `backend/data/saksham_kb/class{N}/{subject}/` | Source curriculum |
| Manifest | `backend/data/saksham_kb/manifest.json` | Chapter catalog; lookup by title or `chapter_id` |
| FAISS | `backend/data/faiss/saksham_index.faiss` | Vectors only |
| Metadata | `backend/data/faiss/saksham_index_meta.json` | Full chunk text per vector (~11 MB) |
| BM25 | `backend/data/faiss/saksham_bm25_index.json` | Lexical sidecar (~16 MB) |
| Index version | `saksham_index_version=v2-section-hybrid` | Bump to force re-ingest |

**Ingest:** `python scripts/ingest_curriculum.py --force`  
**Models offline:** `python scripts/download_models.py --verify`

---

## Graphify knowledge graph

Built 2026-06-13 on `backend/` (AST-only; no LLM semantic layer).

| Output | Purpose |
|--------|---------|
| `graphify-out/graph.json` | Machine-readable graph for `graphify query/path/explain` |
| `graphify-out/GRAPH_REPORT.md` | God nodes, communities, surprising edges |
| `graphify-out/graph.html` | Browser visualization |
| `graphify-out/wiki/` | Human/agent-readable topic articles |

**After code changes:**

```bash
graphify update backend   # AST-only, no API cost
```

**Query examples:**

```bash
graphify query "How does quiz generation connect to retrieval?"
graphify path "generate_saksham_quiz" "get_chapter_chunk_texts"
graphify explain "answer_question"
```

---

## How to navigate this repo

1. **Architecture questions** → `graphify query "…"` or `graphify-out/wiki/index.md`
2. **Broad design** → `backend/ARCHITECTURE.md`
3. **Graph structure** → `graphify-out/GRAPH_REPORT.md` (God Nodes, communities)
4. **Specific symbols** → `graphify explain "<symbol>"` then read source file
5. **Do not** grep the whole repo blindly when `graph.json` exists

---

## Conventions for agents making changes

1. **Minimize scope** — fix the general pipeline, not one-off chapter templates.
2. **Match existing style** in surrounding modules (typing, logging, error types).
3. **Quiz changes** — update tests in `tests/unit/test_quiz_*.py`; run quiz test suite.
4. **Chapter lookup** — use `get_chapter_from_manifest()` / `chapter_matches()`; never slugify the user ref into every chapter’s match set.
5. **Cache** — bump `quiz_cache_version` when output shape or validation changes.
6. **Keep graph current** — `graphify update backend` after substantive edits.
7. **No secrets in git** — `.env` is local; use `.env.example` for new vars.

---

## Known limitations

1. **Small LLM** (`llama3.2:1b`) — weak JSON/long output; quiz uses plain-text LLM format + grounded-first.
2. **OCR in PDFs** — cloze tier can still produce noisy blanks; prefer definitions + LLM.
3. **Exercise-list chunks** — can rank high in retrieval for some question phrasings.
4. **Graph semantic layer** — not built (no `GEMINI_API_KEY`); AST captures imports/calls, not doc concepts from `ARCHITECTURE.md`.

---

## Quick start (local dev)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # configure Ollama URL, models
uvicorn app:app --reload --port 8000
```

**Verify quiz:**

```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{"source":"saksham","class_level":10,"subject":"Science","chapter":"Electricity","question_count":7}'
```

Expect `"chapter_id": "electricity"` and ≥5 questions without `Option N` fillers.

---

## Related documents

| Document | Location |
|----------|----------|
| Full backend architecture | `backend/ARCHITECTURE.md` |
| Graph audit report | `graphify-out/GRAPH_REPORT.md` |
| Quiz pipeline detail | `graphify-out/wiki/quiz-generation.md` |
| Wiki index | `graphify-out/wiki/index.md` |
| Agent entry (all tools) | `AGENTS.md` (repo root) |
