# Hinenglish Localization — Backend Guide

Convert **existing English** Saksham responses into Hinenglish (Devanagari + preserved English terms).  
This endpoint does **not** run RAG — call an English endpoint first, then localize the text.

## Flow

```
POST /ask       → English answer
POST /localize/hi → Hinenglish text (+ optional audio)
```

Same pattern for `/summary`, `/simplify`, and `/quiz`.

---

## POST /localize/hi

### Answer or summary (prose)

```bash
curl -s -X POST "http://localhost:8000/localize/hi" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "• Photosynthesis is the process by which green plants make food using sunlight.",
    "content_type": "answer",
    "class_level": 9,
    "subject": "Science",
    "include_audio": true
  }' | python3 -m json.tool
```

**Response fields:**

| Field | Description |
|-------|-------------|
| `hindi_text` | Hinenglish prose |
| `reading_segments` | Segments for read-along UI |
| `audio_path` | Hindi Piper WAV when `include_audio: true` |
| `cached` | `true` if served from cache |

### Quiz (structured)

```bash
curl -s -X POST "http://localhost:8000/localize/hi" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "quiz",
    "class_level": 8,
    "quiz": {
      "questions": [
        {
          "question": "What is force?",
          "option_a": "Push or pull",
          "option_b": "Color",
          "option_c": "Sound",
          "option_d": "Light",
          "correct_answer": "A"
        }
      ]
    }
  }' | python3 -m json.tool
```

`correct_answer` stays **A/B/C/D** — only question and options are translated.

---

## Hinenglish rules

1. Explanatory text in **Devanagari**
2. Proper nouns unchanged (Louis XVI, Newton)
3. Science terms: `हिंदी (English term)` e.g. प्रकाश संश्लेषण (Photosynthesis)
4. Formulas and units stay in Latin script (H₂O, cm)
5. No new facts — paraphrase English source only

---

## Hindi audio setup

```bash
cd backend
python scripts/download_piper.py --hindi
```

Set in `.env`:

```env
PIPER_HINDI_MODEL_PATH=./data/models/piper/hi_IN-rohan-medium.onnx
```

Bulleted Hinenglish uses point-wise audio with **बिंदु 1**, **बिंदु 2**, etc.

---

## Deprecated: POST /hindi

`POST /hindi` still works but is **deprecated**. It re-runs RAG in Hindi mode and may produce lower quality than:

1. `POST /ask` (English, grounded)
2. `POST /localize/hi` (translate the English answer)

Deprecated responses include `"deprecated": true` and a `Deprecation: true` header.

---

## Settings

```env
LOCALIZE_CACHE_VERSION=v1-hinenglish
OLLAMA_NUM_PREDICT_LOCALIZE=2048
PIPER_HINDI_MODEL_PATH=./data/models/piper/hi_IN-rohan-medium.onnx
```

Uses the same `OLLAMA_MODEL` as other endpoints.

---

## content_type values

| Value | Use with |
|-------|----------|
| `answer` | `POST /ask` → `data.answer` |
| `summary` | `POST /summary` → `data.summary` |
| `simplify` | `POST /simplify` → simplified text |
| `quiz` | `POST /quiz` → `data.questions` |
