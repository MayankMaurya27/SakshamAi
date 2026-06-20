# Saksham AI — Complete Feature Testing Guide

Commands and endpoints to test **every** backend feature.  
Base URL (local): `http://localhost:8000`

> [!TIP]
> **Prefer GUI Testing?** A pre-configured Postman Collection [SakshamAI_Postman_Collection.json](file:///Users/mayankmaurya/Documents/SakshamAi/SakshamAI_Postman_Collection.json) is available at the root of the project. Simply import it into Postman to run these tests with one-click!

---

## Table of contents

1. [Prerequisites](#1-prerequisites)
2. [One-time setup](#2-one-time-setup)
3. [Start the server](#3-start-the-server)
4. [Endpoint index](#4-endpoint-index)
5. [Health & static pages](#5-health--static-pages)
6. [Saksham curriculum browse](#6-saksham-curriculum-browse)
7. [POST /ask — RAG answers](#7-post-ask--rag-answers)
8. [POST /summary — chapter revision notes](#8-post-summary--chapter-revision-notes)
9. [POST /quiz — MCQ generation](#9-post-quiz--mcq-generation)
10. [POST /simplify — simplified answers](#10-post-simplify--simplified-answers)
11. [POST /upload — user PDF pipeline](#11-post-upload--user-pdf-pipeline)
12. [Document management](#12-document-management)
13. [POST /audio — standalone TTS](#13-post-audio--standalone-tts)
14. [Accessibility profiles (dyslexia, beginner, visual)](#14-accessibility-profiles-dyslexia-beginner-visual)
15. [POST /localize/hi — Hinenglish conversion](#15-post-localizehi--hinenglish-conversion)
16. [POST /hindi — deprecated](#16-post-hindi--deprecated)
17. [Edge / PDF-free deployment check](#17-edge--pdf-free-deployment-check)
18. [Automated tests (pytest)](#18-automated-tests-pytest)
19. [OpenAPI docs](#19-openapi-docs)
20. [Troubleshooting](#20-troubleshooting)

---

## 1. Prerequisites

| Requirement | Purpose |
|-------------|---------|
| Python 3.11+ venv | Backend runtime |
| Ollama running | LLM (`llama3.2:1b` default) |
| `data/faiss/` | Pre-built Saksham index (PDF-free OK) |
| `data/models/` | Embedding + optional reranker models |
| Piper model (optional) | English/Hindi TTS when `include_audio: true` |

```bash
# Verify Ollama
curl -s http://localhost:11434/api/tags | python3 -m json.tool

# Verify pre-built index loaded (after server start — see logs)
# "Using pre-built Saksham index (14750 vectors); PDFs not required at runtime"
```

---

## 2. One-time setup

Run from `backend/` with venv activated:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit paths as needed
```

### Embedding & reranker models (offline / Jetson)

```bash
python scripts/download_models.py --verify
python scripts/download_models.py --cleanup --verify   # optional: remove ONNX extras
```

### Piper TTS — English

```bash
python scripts/download_piper.py
# Set in .env: PIPER_MODEL_PATH=./data/models/piper/en_US-lessac-medium.onnx
```

### Piper TTS — Hindi (for `/localize/hi` + `include_audio`)

```bash
python scripts/download_piper.py --hindi
# Set in .env: PIPER_HINDI_MODEL_PATH=./data/models/piper/hi_IN-rohan-medium.onnx
```

### Curriculum index (only when PDFs change)

PDFs are **not** required at runtime if `data/faiss/` + `manifest.json` + hash exist.

```bash
# After adding/replacing PDFs under data/saksham_kb/
python scripts/ingest_curriculum.py --force

# PDF-free edge deploy: delete PDFs, then update hash
find data/saksham_kb/class6 data/saksham_kb/class7 data/saksham_kb/class8 \
  data/saksham_kb/class9 data/saksham_kb/class10 -name "*.pdf" -delete
python3 -c "
from config.settings import get_settings
from services.knowledge_service import compute_curriculum_hash
get_settings().saksham_kb_hash_path.write_text(compute_curriculum_hash())
print('Hash updated')
"
```

### Other maintenance scripts

```bash
python scripts/build_saksham_index.py          # same as ingest (no --force = load if hash OK)
python scripts/build_saksham_index.py --force  # full rebuild from PDFs
python scripts/purge_uploads.py                # clear uploaded PDFs + user index
```

---

## 3. Start the server

```bash
cd backend
source .venv/bin/activate
uvicorn app:app --reload --port 8000
```

Pretty-print JSON responses (recommended):

```bash
alias pj='python3 -m json.tool'
```

---

## 4. Endpoint index

| Method | Path | Feature |
|--------|------|---------|
| GET | `/health` | Health check |
| GET | `/dyslexia-demo` | Redirect to dyslexia UI demo |
| GET | `/static/dyslexia_demo.html` | Dyslexia demo page |
| GET | `/audio/{filename}` | Serve generated WAV files |
| GET | `/saksham/classes` | List classes 6–10 |
| GET | `/saksham/subjects` | Subjects for a class |
| GET | `/saksham/chapters` | Chapters for class + subject |
| GET | `/saksham/topics` | Chapter titles (alias) |
| POST | `/ask` | RAG Q&A (Saksham or upload) |
| POST | `/summary` | Revision summary |
| POST | `/quiz` | MCQ quiz |
| POST | `/simplify` | Simplified explanation |
| POST | `/upload` | Upload user PDF |
| GET | `/documents` | List uploads |
| GET | `/document/{id}` | Upload detail + stored quizzes |
| DELETE | `/document/{id}` | Delete upload + index vectors |
| POST | `/audio` | Standalone text-to-speech |
| POST | `/localize/hi` | English → Hinenglish |
| POST | `/hindi` | **Deprecated** — use `/ask` + `/localize/hi` |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |

---

## 5. Health & static pages

```bash
curl -s http://localhost:8000/health | pj

# Browser: dyslexia demo
open http://localhost:8000/dyslexia-demo
# or
open http://localhost:8000/static/dyslexia_demo.html
```

---

## 6. Saksham curriculum browse

```bash
# All class levels
curl -s "http://localhost:8000/saksham/classes" | pj

# Subjects for Class 8
curl -s "http://localhost:8000/saksham/subjects?class_level=8" | pj

# Chapters for Class 8 Science
curl -s "http://localhost:8000/saksham/chapters?class_level=8&subject=Science" | pj

# Topics alias (titles only)
curl -s "http://localhost:8000/saksham/topics?class_level=10&subject=Science" | pj
```

**Class 9 note:** subjects are split (Economics, Geography, History, Mathematics, Political Science, Science) — not "Social Science".

---

## 7. POST /ask — RAG answers

### Saksham curriculum (default learn mode)

```bash
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is force?",
    "source": "saksham",
    "class_level": 8,
    "subject": "Science",
    "chapter": "Exploring Forces"
  }' | pj
```

### Ask modes (`mode` field)

| `mode` | Effect |
|--------|--------|
| `learn` | Default grounded answer |
| `beginner` | Simpler language |
| `dyslexia` | Dyslexia prompt (use `accessibility_profile` for formatting + audio) |
| `visual` | Visual-learning prompt |
| `simplify` | Prefer `POST /simplify` |
| `hindi` | Prefer `POST /localize/hi` |

```bash
# Beginner mode via mode field
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is photosynthesis?",
    "source": "saksham",
    "class_level": 7,
    "subject": "Science",
    "chapter": "Nutrition in Plants",
    "mode": "beginner"
  }' | pj

# Visual mode
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain electric circuits.",
    "source": "saksham",
    "class_level": 10,
    "subject": "Science",
    "chapter": "Electricity",
    "mode": "visual"
  }' | pj
```

### Uploaded document

Replace `DOCUMENT_ID` after `/upload`:

```bash
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic of this document?",
    "source": "document",
    "document_id": DOCUMENT_ID
  }' | pj
```

### With audio (`include_audio: true`)

```bash
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is force?",
    "source": "saksham",
    "class_level": 8,
    "subject": "Science",
    "chapter": "Exploring Forces",
    "include_audio": true
  }' | pj
# Play: http://localhost:8000{audio_path from response}
```

### Validation errors (expect 422 / 404)

```bash
# Empty question → 422
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"","source":"document"}' | pj

# Saksham without chapter fields → 422
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is force?","source":"saksham"}' | pj

# Missing document → 404
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"Hi","source":"document","document_id":99999}' | pj
```

---

## 8. POST /summary — chapter revision notes

### Saksham chapter

```bash
curl -s -X POST "http://localhost:8000/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "saksham",
    "class_level": 10,
    "subject": "Science",
    "chapter": "Electricity"
  }' | pj
```

### Regenerate (bypass cache)

```bash
curl -s -X POST "http://localhost:8000/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "saksham",
    "class_level": 8,
    "subject": "Science",
    "chapter": "Exploring Forces",
    "regenerate": true
  }' | pj
```

### Uploaded document summary

```bash
curl -s -X POST "http://localhost:8000/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "document",
    "document_id": DOCUMENT_ID
  }' | pj
```

Response includes `summary`, `format_version`, `cached`, and optional `accessibility` block.

---

## 9. POST /quiz — MCQ generation

### Saksham quiz (5–15 questions)

```bash
curl -s -X POST "http://localhost:8000/quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "saksham",
    "class_level": 8,
    "subject": "Science",
    "chapter": "Exploring Forces",
    "question_count": 5
  }' | pj
```

### Document quiz

```bash
curl -s -X POST "http://localhost:8000/quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "document",
    "document_id": DOCUMENT_ID,
    "question_count": 10
  }' | pj
```

Each question: `question`, `option_a`–`option_d`, `correct_answer` (A/B/C/D).

---

## 10. POST /simplify — simplified answers

```bash
curl -s -X POST "http://localhost:8000/simplify" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain democracy and republic.",
    "source": "saksham",
    "class_level": 7,
    "subject": "Social Science",
    "chapter": "The State, the Government, and You"
  }' | pj
```

Response key: `simplified_answer` (plus optional `accessibility`).

---

## 11. POST /upload — user PDF pipeline

Upload runs: PDF extract → chunk → FAISS user index → **grounded summary** → auto-analysis quiz seed.

```bash
curl -s -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/your/chapter.pdf" | pj
```

Save `document_id` from response. Response includes:

- `document_id`
- `summary` (grounded prose)
- `format_version`
- `key_concepts` (currently empty list at upload; concepts live in summary pipeline)
- `quiz_count` (auto-generated MCQs stored in DB)

### Upload validation

```bash
# Non-PDF → 422
curl -s -X POST "http://localhost:8000/upload" \
  -F "file=@/tmp/test.txt" | pj

# Empty file → 422
curl -s -X POST "http://localhost:8000/upload" \
  -F "file=@/tmp/empty.pdf;type=application/pdf" | pj
```

---

## 12. Document management

```bash
# List all uploads
curl -s "http://localhost:8000/documents" | pj

# Detail + quizzes created at upload
curl -s "http://localhost:8000/document/DOCUMENT_ID" | pj

# Delete upload, PDF file, and FAISS vectors
curl -s -X DELETE "http://localhost:8000/document/DOCUMENT_ID" | pj
```

---

## 13. POST /audio — standalone TTS

English Piper (default):

```bash
curl -s -X POST "http://localhost:8000/audio" \
  -H "Content-Type: application/json" \
  -d '{"text":"Force is a push or pull on an object."}' | pj
```

Response: `audio_path` (e.g. `/audio/abc123.wav`). Play:

```bash
open "http://localhost:8000/audio/FILENAME.wav"
```

---

## 14. Accessibility profiles (dyslexia, beginner, visual)

Set `"accessibility_profile": "dyslexia" | "beginner" | "visual"` on:

- `POST /ask`
- `POST /summary`
- `POST /quiz`
- `POST /simplify`
- `POST /hindi` (deprecated)

Profile **overrides** the prompt mode and adds an `accessibility` block:

```json
"accessibility": {
  "profile": "dyslexia",
  "display_hints": { "prefer_audio": true, ... },
  "reading_segments": ["Point 1 text", "Point 2 text"],
  "audio_path": "/audio/....wav"
}
```

### Dyslexia + point-wise audio

```bash
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is photosynthesis?",
    "source": "saksham",
    "class_level": 7,
    "subject": "Science",
    "chapter": "Nutrition in Plants",
    "accessibility_profile": "dyslexia",
    "include_audio": true
  }' | pj
```

### Dyslexia summary

```bash
curl -s -X POST "http://localhost:8000/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "saksham",
    "class_level": 8,
    "subject": "Science",
    "chapter": "Exploring Forces",
    "accessibility_profile": "dyslexia",
    "include_audio": true
  }' | pj
```

### Dyslexia quiz

```bash
curl -s -X POST "http://localhost:8000/quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "saksham",
    "class_level": 8,
    "subject": "Science",
    "chapter": "Light- Mirrors and Lenses",
    "question_count": 5,
    "accessibility_profile": "dyslexia"
  }' | pj
```

### Beginner profile on ask

```bash
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is gravity?",
    "source": "saksham",
    "class_level": 9,
    "subject": "Science",
    "chapter": "Gravitation",
    "accessibility_profile": "beginner"
  }' | pj
```

More dyslexia examples: see `docs/DYSLEXIA_TEST.md`.

---

## 15. POST /localize/hi — Hinenglish conversion

**Flow:** get English from `/ask`, `/summary`, `/simplify`, or `/quiz` → send text to `/localize/hi`.

Does **not** run RAG — translate-only.

### Localize an answer

```bash
curl -s -X POST "http://localhost:8000/localize/hi" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "• Photosynthesis is the process by which green plants make food using sunlight.",
    "content_type": "answer",
    "class_level": 9,
    "include_audio": false
  }' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['hindi_text'])"
```

### Multi-line answer (use Python to build valid JSON)

```bash
python3 <<'PY' | curl -s -X POST "http://localhost:8000/localize/hi" \
  -H "Content-Type: application/json" -d @- | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['hindi_text'])"
import json
print(json.dumps({
  "text": open("/tmp/answer.txt").read(),
  "content_type": "answer",
  "class_level": 9,
  "include_audio": True,
}))
PY
```

### Localize summary text

```bash
curl -s -X POST "http://localhost:8000/localize/hi" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Electric current flows through a closed circuit. Resistance limits current flow.",
    "content_type": "summary",
    "class_level": 10
  }' | pj
```

### Localize simplified text

```bash
curl -s -X POST "http://localhost:8000/localize/hi" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Democracy means people choose leaders by voting.",
    "content_type": "simplify",
    "class_level": 7
  }' | pj
```

### Localize quiz (structured)

```bash
curl -s -X POST "http://localhost:8000/localize/hi" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "quiz",
    "class_level": 8,
    "quiz": {
      "questions": [{
        "question": "What is force?",
        "option_a": "Push or pull",
        "option_b": "Color",
        "option_c": "Sound",
        "option_d": "Light",
        "correct_answer": "A"
      }]
    }
  }' | pj
```

`content_type` values: `answer` | `summary` | `simplify` | `quiz`.

Hindi audio: set `"include_audio": true` and configure `PIPER_HINDI_MODEL_PATH`.

Full Hinenglish rules: `docs/HINDI_LOCALIZE.md`.

---

## 16. POST /hindi — deprecated

Still callable but returns `Deprecation: true` header and migration message. Prefer English endpoint + `/localize/hi`.

```bash
curl -s -D - -X POST "http://localhost:8000/hindi" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is force?",
    "source": "saksham",
    "class_level": 8,
    "subject": "Science",
    "chapter": "Exploring Forces"
  }' | pj
```

---

## 17. Edge / PDF-free deployment check

After removing PDFs from `data/saksham_kb/class6` … `class10`:

```bash
cd backend
source .venv/bin/activate

# 1. No PDFs on disk
find data/saksham_kb -name "*.pdf" | wc -l   # expect 0

# 2. Index + manifest present
ls -lh data/faiss/saksham_index.faiss data/faiss/saksham_index_meta.json data/saksham_kb/manifest.json

# 3. Startup loads without re-ingest
uvicorn app:app --port 8000
# Log: "Using pre-built Saksham index (... vectors); PDFs not required at runtime"

# 4. Spot-check Class 8 Science (previously missing — should work now)
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is force?",
    "source": "saksham",
    "class_level": 8,
    "subject": "Science",
    "chapter": "Exploring Forces"
  }' | pj

# 5. Full chapter count
curl -s "http://localhost:8000/saksham/chapters?class_level=8&subject=Science" | pj
```

**Jetson bundle:** copy `data/faiss/`, `data/saksham_kb/manifest.json`, `data/models/`, code, `.env` — PDFs optional.

---

## 18. Automated tests (pytest)

```bash
cd backend
source .venv/bin/activate

# Full suite
pytest

# API tests (all endpoints)
pytest tests/api/ -v

# By feature
pytest tests/api/test_ask_api.py -v
pytest tests/api/test_summary_api.py -v
pytest tests/api/test_quiz_api.py -v
pytest tests/api/test_upload_api.py -v
pytest tests/api/test_documents_api.py -v
pytest tests/api/test_dyslexia_api.py -v
pytest tests/api/test_localize_api.py -v

# Integration (needs Ollama for some tests)
pytest tests/integration/ -v

# Knowledge base / PDF-free index
pytest tests/unit/test_prebuilt_index.py tests/unit/test_knowledge_service.py -v

# Quiz quality gates
pytest tests/unit/test_quiz_*.py -v
```

---

## 19. OpenAPI docs

Interactive API explorer (all request schemas):

```
http://localhost:8000/docs
http://localhost:8000/redoc
```

---

## 20. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `503 Ollama is not available` | Start Ollama: `ollama serve` ; pull model: `ollama pull llama3.2:1b` |
| `422` on Saksham endpoints | Provide `class_level`, `subject`, `chapter` |
| `No indexed content for chapter` | Run `ingest_curriculum.py --force` or fix manifest/index mismatch |
| Server re-indexes after PDF delete | Update `data/faiss/saksham_kb_hash.txt` (see §2) |
| `audio_path: null` | Install Piper; set `PIPER_MODEL_PATH` / `PIPER_HINDI_MODEL_PATH` |
| Hindi localize JSON curl fails | Use Python `json.dumps` for multi-line text (see §15) |
| Slow first request | Embedding model preload on startup; first LLM call warms Ollama |
| Quiz cache stale | Bump `QUIZ_CACHE_VERSION` in `.env` and restart |
| Summary cache stale | Bump `SUMMARY_CACHE_VERSION` in `.env` and restart |

---

## Quick end-to-end smoke test (copy-paste)

```bash
BASE=http://localhost:8000

curl -s $BASE/health | pj

curl -s "$BASE/saksham/chapters?class_level=8&subject=Science" | pj

curl -s -X POST "$BASE/ask" -H "Content-Type: application/json" \
  -d '{"question":"What is force?","source":"saksham","class_level":8,"subject":"Science","chapter":"Exploring Forces"}' | pj

curl -s -X POST "$BASE/summary" -H "Content-Type: application/json" \
  -d '{"source":"saksham","class_level":10,"subject":"Science","chapter":"Electricity"}' | pj

curl -s -X POST "$BASE/quiz" -H "Content-Type: application/json" \
  -d '{"source":"saksham","class_level":8,"subject":"Science","chapter":"Exploring Forces","question_count":5}' | pj

curl -s -X POST "$BASE/localize/hi" -H "Content-Type: application/json" \
  -d '{"text":"Force is a push or pull.","content_type":"answer","class_level":8}' | pj
```

---

*Last updated for Saksham AI backend v1.0 — NCERT Classes 6–10, PDF-free edge deploy, Hinenglish localize, dyslexia mode, Piper TTS.*
