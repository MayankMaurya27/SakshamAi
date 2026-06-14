# API Endpoints

**Entry:** `backend/app.py` (FastAPI)  
**Schemas:** `backend/api/schemas.py`

## Core routes

| Method | Path | Module | Purpose |
|--------|------|--------|---------|
| POST | `/ask` | `api/ask.py` | RAG Q&A (saksham or document) |
| POST | `/quiz` | `api/quiz.py` | MCQ quiz generation |
| POST | `/upload` | `api/upload.py` | User PDF upload + index |
| GET | `/saksham/chapters` | `api/saksham.py` | List curriculum chapters |
| POST | `/summary` | `api/summary.py` | Chapter/document summary |
| POST | `/simplify` | `api/simplify.py` | Simplified explanation |
| POST | `/audio` | `api/audio.py` | TTS (Piper) |

## Quiz request

```json
{
  "source": "saksham",
  "class_level": 10,
  "subject": "Science",
  "chapter": "Electricity",
  "question_count": 7
}
```

**Response fields:** `questions[]`, `chapter_id`, `chapter`, `class_level`, `subject`, `question_count`.

Document quiz: `"source": "document", "document_id": 1`.

## Error types

From `backend/exceptions.py`: `ValidationError` (422), `DocumentNotFoundError` (404), `SakshamError`, `ServiceUnavailableError`.

## Graph

```bash
graphify explain "create_quiz"
graphify path "create_quiz" "generate_quiz"
```
