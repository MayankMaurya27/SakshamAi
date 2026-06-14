# Summary Generation Flow

Unified pipeline for **Learn from Saksham** and **uploaded documents**.  
Both paths call `generate_summary_from_chunks()` in `services/summary_service.py`.

| Entry | Function chain |
|-------|----------------|
| `POST /summary` (saksham) | `generate_saksham_summary()` → cache check → chunks from FAISS → `generate_summary_from_chunks()` |
| `POST /upload` | `process_upload()` → chunks in SQLite → **`save_document_summary_from_chunks()`** → `generate_summary_from_chunks()` |
| `POST /summary` (document) | `generate_document_summary()` → DB cache check → chunks from SQLite → **`save_document_summary_from_chunks()`** → `generate_summary_from_chunks()` |

Upload and document `/summary` both persist via `save_document_summary_from_chunks()`.

## End-to-end flowchart

```mermaid
flowchart TD
    subgraph entry [Entry points]
        A1["POST /summary<br/>source=saksham"]
        A2["POST /upload<br/>PDF file"]
        A3["POST /summary<br/>source=document"]
    end

    subgraph load [Load content]
        B1["Validate chapter<br/>manifest + FAISS chunks"]
        B2["PDF → text → chunks<br/>FAISS user index + SQLite"]
        B3["Load chunks from SQLite<br/>by document_id"]
    end

    subgraph cache [Cache / stored summary]
        C1{"Saksham file cache hit?<br/>regenerate=false"}
        C2{"Document summary in DB?<br/>regenerate=false"}
    end

    subgraph shared ["Shared pipeline: generate_summary_from_chunks()"]
        D1["filter_summary_source_chunks()<br/>drop exercises, activities, narratives"]
        D2["prepare_summary_context()<br/>join factual chunks ≤6500 chars"]
        D3{"Context fits<br/>one pass?"}
        D4["LLM full summary<br/>Ollama offline"]
        D5["Map-reduce:<br/>partial LLM × windows"]
        D6["LLM synthesis<br/>merge partials"]
        D7["_finalize_summary()<br/>clean → ground → expand if long chapter"]
        D8{"Usable length<br/>+ grounded?"}
        D9["Fallback: definition summary<br/>or minimal source excerpt"]
        D10["build_minimal_source_summary()<br/>factual sentences from source only"]
    end

    subgraph persist [Persist and respond]
        E1["Save Saksham file cache"]
        E2["Save summary to documents.summary"]
        E3["AUTO_ANALYSIS JSON<br/>quiz questions only at upload"]
        OUT["JSON response<br/>summary + format_version + source"]
    end

    A1 --> B1 --> C1
    A2 --> B2
    A3 --> B3 --> C2

    C1 -->|yes| OUT
    C2 -->|yes| OUT

    C1 -->|no| PIPE
    C2 -->|no| PIPE
    B2 --> SAVE

    SAVE["save_document_summary_from_chunks()"] --> PIPE
    PIPE["generate_summary_from_chunks()"] --> D1

    D1 --> D2 --> D3
    D3 -->|yes| D4 --> D7
    D3 -->|no| D5 --> D6 --> D7
    D7 --> D8
    D8 -->|no, long chapter| D9 --> D8
    D8 -->|no, short doc| D10 --> D8
    D8 -->|still empty| D10

    D8 -->|yes| PERSIST
    PERSIST{"Source?"}
    PERSIST -->|saksham| E1 --> OUT
    PERSIST -->|upload| E2 --> E3 --> OUT
    PERSIST -->|document /summary| E2 --> OUT
```

## Upload vs Saksham (what is identical)

| Step | Saksham | Upload / document |
|------|---------|-------------------|
| Core function | `generate_summary_from_chunks()` | Same |
| Pre-filter | `filter_summary_source_chunks()` | Same |
| LLM prompt | Ollama prose summary | Same |
| Grounding | `ground_summary_text()` | Same |
| Short-doc fallback | `build_minimal_source_summary()` | Same |
| Long-chapter fallback | Definition-based fallback | Same |
| Cache / store | File cache per chapter | SQLite `documents.summary` |
| Quiz | Separate `POST /quiz` | AUTO_ANALYSIS at upload (questions only) |

## Response shape

```json
{
  "summary": "Paragraph one...\n\nParagraph two...",
  "format_version": "v2-prose",
  "source": "saksham",
  "cached": false
}
```

Render `summary` with paragraph breaks (`\n\n` or CSS `white-space: pre-line`).

## Key settings (`.env`)

| Variable | Purpose |
|----------|---------|
| `SUMMARY_MAX_CONTEXT_CHARS` | Single-pass vs map-reduce threshold (~6500) |
| `SUMMARY_MIN_WORDS` / `SUMMARY_TARGET_WORDS` | Length targets for full chapters |
| `OLLAMA_NUM_PREDICT_SUMMARY` | Max tokens for summary LLM calls |
| `SUMMARY_CACHE_VERSION` | Bust Saksham file cache when pipeline changes |

## Key files

| File | Role |
|------|------|
| `api/summary.py` | HTTP endpoint |
| `documents/processor.py` | Upload → `save_document_summary_from_chunks()` |
| `services/summary_service.py` | Orchestration, cache, unified chunk pipeline |
| `services/summary_context.py` | Chunk filtering + context assembly |
| `services/summary_factual.py` | Narrative strip + sentence grounding |
| `services/summary_parser.py` | Clean / dedupe prose |
| `services/summary_grounded.py` | Definition fallback + minimal source excerpt |
| `ai/prompt_builder.py` | LLM prompts |
