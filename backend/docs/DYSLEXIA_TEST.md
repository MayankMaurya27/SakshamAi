# Dyslexia Mode — Testing Guide

Dyslexia mode uses a **deterministic formatter** (short bullets) plus optional **Piper TTS**.  
Set `"accessibility_profile": "dyslexia"` on supported endpoints.

## Browser demo

Open after starting the server:

```
http://localhost:8000/dyslexia-demo
```

Or:

```
http://localhost:8000/static/dyslexia_demo.html
```

---

## POST /ask (Saksham + dyslexia)

```bash
curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d '{"question":"What is photosynthesis?","source":"saksham","class_level":7,"subject":"Science","chapter":"Nutrition in Plants","accessibility_profile":"dyslexia"}'
```

## POST /ask (document + dyslexia + audio)

Replace `1` with your `document_id`:

```bash
curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d '{"question":"What is force?","source":"document","document_id":1,"accessibility_profile":"dyslexia","include_audio":true}'
```

---

## POST /simplify (dyslexia)

```bash
curl -X POST "http://localhost:8000/simplify" -H "Content-Type: application/json" -d '{"question":"Explain democracy","source":"saksham","class_level":7,"subject":"Social Science","chapter":"The State, the Government, and You","accessibility_profile":"dyslexia"}'
```

---

## POST /hindi (dyslexia — Hindi LLM + bullet formatter)

```bash
curl -X POST "http://localhost:8000/hindi" -H "Content-Type: application/json" -d '{"question":"What is photosynthesis?","source":"saksham","class_level":7,"subject":"Science","chapter":"Nutrition in Plants","accessibility_profile":"dyslexia"}'
```

---

## POST /summary (Saksham + dyslexia)

```bash
curl -X POST "http://localhost:8000/summary" -H "Content-Type: application/json" -d '{"source":"saksham","class_level":7,"subject":"Social Science","chapter":"The State, the Government, and You","accessibility_profile":"dyslexia"}'
```

## POST /summary (document + dyslexia)

```bash
curl -X POST "http://localhost:8000/summary" -H "Content-Type: application/json" -d '{"source":"document","document_id":1,"accessibility_profile":"dyslexia","include_audio":true}'
```

---

## POST /quiz (Saksham + dyslexia)

```bash
curl -X POST "http://localhost:8000/quiz" -H "Content-Type: application/json" -d '{"source":"saksham","class_level":7,"subject":"Science","chapter":"Nutrition in Plants","question_count":5,"accessibility_profile":"dyslexia"}'
```

---

## POST /audio (standalone TTS)

```bash
curl -X POST "http://localhost:8000/audio" -H "Content-Type: application/json" -d '{"text":"The Sun is a star. Earth moves around the Sun."}'
```

---

## Expected response shape (when dyslexia profile is set)

```json
{
  "success": true,
  "data": {
    "answer": "• Photosynthesis (how plants make food) uses sunlight.\n\n• Chlorophyll traps light energy.",
    "accessibility": {
      "profile": "dyslexia",
      "display_hints": {
        "line_height": 1.5,
        "max_line_chars": 60,
        "font_family": "sans-serif",
        "letter_spacing": "0.03em",
        "word_spacing": "0.05em",
        "background": "#FFF8E7",
        "prefer_audio": true
      },
      "reading_segments": ["Photosynthesis (how plants make food) uses sunlight.", "Chlorophyll traps light energy."],
      "audio_path": null
    }
  }
}
```

`audio_path` is set when `include_audio: true` and Piper is configured (`PIPER_MODEL_PATH`).

---

## Settings (`.env`)

```env
DYSLEXIA_MAX_WORDS_PER_SENTENCE=15
DYSLEXIA_MAX_BULLETS=8
```
