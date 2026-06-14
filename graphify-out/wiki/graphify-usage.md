# Using the Knowledge Graph

## Files

| File | Use |
|------|-----|
| `graphify-out/graph.json` | Query/path/explain input |
| `graphify-out/GRAPH_REPORT.md` | God nodes, communities, cycles |
| `graphify-out/graph.html` | Visual exploration in browser |
| `graphify-out/PROJECT_CONTEXT.md` | Human handoff + recent changes |

## Commands (run from repo root)

```bash
graphify query "How does quiz generation work?"
graphify path "generate_saksham_quiz" "get_chapter_chunk_texts"
graphify explain "answer_question"
graphify update backend    # after code edits (AST, free)
```

## For AI agents (any tool)

1. Check `graphify-out/graph.json` exists
2. Run `graphify query "<your question>"` before broad grep/read
3. Read source files only after the graph orients you
4. After edits: `graphify update backend`

## Build info

- **Built:** 2026-06-13 on `backend/`
- **Method:** AST extraction (1126 nodes, 2240 edges, 63 communities)
- **Semantic layer:** not run (no LLM API key); code structure only
- **To add doc semantics:** set `GEMINI_API_KEY` and re-run `/graphify backend`

## Cursor-specific (optional)

- `.cursor/rules/graphify.mdc` — always-on rule to query graph first
- `.cursor/skills/graphify/` — full `/graphify` rebuild skill

Other tools should read `AGENTS.md` and `graphify-out/PROJECT_CONTEXT.md` instead.
