# Graph Report - Saksham AI backend (2026-06-13)

> **Agent handoff:** For full project context, recent quiz pipeline changes, and cross-tool instructions, read **[PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)** and **[wiki/index.md](wiki/index.md)**. Root **[AGENTS.md](../AGENTS.md)** is the entry point for GitHub Copilot, Antigravity, Codex, etc.

| Quick links | |
|-------------|---|
| Project overview + recent updates | [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) |
| Quiz generation overhaul | [wiki/quiz-generation.md](wiki/quiz-generation.md) |
| RAG / retrieval | [wiki/retrieval-rag.md](wiki/retrieval-rag.md) |
| API routes | [wiki/api-endpoints.md](wiki/api-endpoints.md) |
| How to query this graph | [wiki/graphify-usage.md](wiki/graphify-usage.md) |
| Full backend architecture | [../backend/ARCHITECTURE.md](../backend/ARCHITECTURE.md) |

---

## Corpus Check
- Large corpus: 96 files · ~4,063,170 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 1126 nodes · 2240 edges · 63 communities (61 shown, 2 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 258 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Quiz Generation|Quiz Generation]]
- [[_COMMUNITY_Quiz Generation|Quiz Generation]]
- [[_COMMUNITY_Activity Formatting|Activity Formatting]]
- [[_COMMUNITY_FAISS Index|FAISS Index]]
- [[_COMMUNITY_Knowledge Service|Knowledge Service]]
- [[_COMMUNITY_Quiz Generation|Quiz Generation]]
- [[_COMMUNITY_Test Prompt Builder|Test Prompt Builder]]
- [[_COMMUNITY_Question Router|Question Router]]
- [[_COMMUNITY_App|App]]
- [[_COMMUNITY_RAG Service|RAG Service]]
- [[_COMMUNITY_BM25 Search|BM25 Search]]
- [[_COMMUNITY_Embeddings|Embeddings]]
- [[_COMMUNITY_Conftest|Conftest]]
- [[_COMMUNITY_Curriculum Utils|Curriculum Utils]]
- [[_COMMUNITY_Reranker|Reranker]]
- [[_COMMUNITY_Knowledge Service|Knowledge Service]]
- [[_COMMUNITY_Init|  Init  ]]
- [[_COMMUNITY_Llm|Llm]]
- [[_COMMUNITY_Quiz Generation|Quiz Generation]]
- [[_COMMUNITY_Exceptions|Exceptions]]
- [[_COMMUNITY_Saksham|Saksham]]
- [[_COMMUNITY_Download Models|Download Models]]
- [[_COMMUNITY_Quiz Generation|Quiz Generation]]
- [[_COMMUNITY_Chunker|Chunker]]
- [[_COMMUNITY_Quiz Generation|Quiz Generation]]
- [[_COMMUNITY_Test Accessibility Service|Test Accessibility Service]]
- [[_COMMUNITY_Retrieval Pipeline|Retrieval Pipeline]]
- [[_COMMUNITY_Retrieval Pipeline|Retrieval Pipeline]]
- [[_COMMUNITY_Bio Formatter|Bio Formatter]]
- [[_COMMUNITY_Constants|Constants]]
- [[_COMMUNITY_Test Content Refs|Test Content Refs]]
- [[_COMMUNITY_Test Upload Flow|Test Upload Flow]]
- [[_COMMUNITY_Processor|Processor]]
- [[_COMMUNITY_Repositories|Repositories]]
- [[_COMMUNITY_Test Answer Formatter|Test Answer Formatter]]
- [[_COMMUNITY_Test Upload Api|Test Upload Api]]
- [[_COMMUNITY_Embeddings|Embeddings]]
- [[_COMMUNITY_Retrieval Pipeline|Retrieval Pipeline]]
- [[_COMMUNITY_Repositories|Repositories]]
- [[_COMMUNITY_Test Saksham Retrieval|Test Saksham Retrieval]]
- [[_COMMUNITY_Retrieval Pipeline|Retrieval Pipeline]]
- [[_COMMUNITY_Test Pdf Parser|Test Pdf Parser]]
- [[_COMMUNITY_Hybrid Search|Hybrid Search]]
- [[_COMMUNITY_Repositories|Repositories]]
- [[_COMMUNITY_Retrieval Pipeline|Retrieval Pipeline]]
- [[_COMMUNITY_Test Ask Api|Test Ask Api]]
- [[_COMMUNITY_Test Documents Api|Test Documents Api]]
- [[_COMMUNITY_Quiz Generation|Quiz Generation]]
- [[_COMMUNITY_Test Learning Modes|Test Learning Modes]]
- [[_COMMUNITY_Test Repositories|Test Repositories]]
- [[_COMMUNITY_Retrieval Pipeline|Retrieval Pipeline]]
- [[_COMMUNITY_Audio Service|Audio Service]]
- [[_COMMUNITY_Repositories|Repositories]]
- [[_COMMUNITY_API Endpoints|API Endpoints]]
- [[_COMMUNITY_Test Rag Saksham|Test Rag Saksham]]
- [[_COMMUNITY_Seed Kb|Seed Kb]]
- [[_COMMUNITY_Llm|Llm]]
- [[_COMMUNITY_Ingest Curriculum|Ingest Curriculum]]
- [[_COMMUNITY_Knowledge Service|Knowledge Service]]
- [[_COMMUNITY_Db|Db]]
- [[_COMMUNITY_Manifest|Manifest]]
- [[_COMMUNITY_Knowledge Service|Knowledge Service]]

## God Nodes (most connected - your core abstractions)
1. `answer_question()` - 34 edges
2. `ValidationError` - 33 edges
3. `DocumentRepository` - 32 edges
4. `FaissManager` - 28 edges
5. `SakshamError` - 25 edges
6. `ChunkRepository` - 24 edges
7. `DocumentNotFoundError` - 24 edges
8. `try_format_activity_answer()` - 23 edges
9. `LearningMode` - 23 edges
10. `build_saksham_index()` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Session` --uses--> `Base`  [INFERRED]
  backend/database/db.py → backend/database/models.py
- `LearningMode` --uses--> `ActivityIntent`  [INFERRED]
  backend/services/rag_service.py → backend/ai/activity_formatter.py
- `Session` --uses--> `ActivityIntent`  [INFERRED]
  backend/services/rag_service.py → backend/ai/activity_formatter.py
- `SourceType` --uses--> `ActivityIntent`  [INFERRED]
  backend/services/rag_service.py → backend/ai/activity_formatter.py
- `_should_use_keyword_only_retrieval()` --calls--> `is_bio_question()`  [INFERRED]
  backend/ai/retriever.py → backend/ai/bio_formatter.py

## Import Cycles
- 1-file cycle: `backend/app.py -> backend/app.py`
- 2-file cycle: `backend/api/upload.py -> backend/app.py -> backend/api/upload.py`
- 2-file cycle: `backend/api/summary.py -> backend/app.py -> backend/api/summary.py`
- 2-file cycle: `backend/api/hindi.py -> backend/app.py -> backend/api/hindi.py`
- 2-file cycle: `backend/api/ask.py -> backend/app.py -> backend/api/ask.py`
- 2-file cycle: `backend/api/audio.py -> backend/app.py -> backend/api/audio.py`
- 2-file cycle: `backend/api/documents.py -> backend/app.py -> backend/api/documents.py`
- 2-file cycle: `backend/api/quiz.py -> backend/app.py -> backend/api/quiz.py`
- 2-file cycle: `backend/api/saksham.py -> backend/app.py -> backend/api/saksham.py`
- 2-file cycle: `backend/api/simplify.py -> backend/app.py -> backend/api/simplify.py`

## Communities (63 total, 2 thin omitted)

### Community 0 - "Quiz Generation"
Cohesion: 0.06
Nodes (62): Any, Any, QuestionSourceType, _attach_meta(), build_grounded_chapter_questions(), _build_mcq(), _candidate_phrases(), _chunk_windows() (+54 more)

### Community 1 - "Quiz Generation"
Cohesion: 0.07
Nodes (54): Any, _approx_equal(), build_chapter_quiz_questions(), build_concept_questions(), build_definition_questions(), build_fact_questions(), build_triangle_inequality_questions(), detect_math_chapter_kind() (+46 more)

### Community 2 - "Activity Formatting"
Cohesion: 0.06
Nodes (52): _action_before_questions(), ActivityIntent, _clean_step_text(), _dedupe_procedure_steps(), detect_activity_intent(), _extract_activity_explanation(), _extract_aim(), _extract_bullet_steps() (+44 more)

### Community 3 - "FAISS Index"
Cohesion: 0.06
Nodes (33): FaissManager, get_user_index(), Search only vectors whose metadata passes filter_fn., Persist index and metadata to disk., Load index and metadata from disk. Returns True if successful., Return number of vectors in the index., Return singleton user document FAISS index., Manage a single FAISS index with ID metadata mapping. (+25 more)

### Community 4 - "Knowledge Service"
Cohesion: 0.10
Nodes (34): Any, FaissManager, ndarray, Path, ChapterInfo, build_saksham_index(), _chapter_key(), _discovered_chapter_keys() (+26 more)

### Community 5 - "Quiz Generation"
Cohesion: 0.11
Nodes (35): Any, Attach LLM source metadata for downstream verification., tag_llm_questions(), is_math_subject(), Return True when the subject is a mathematics course., _build_response_payload(), _coerce_question_list(), _context_for_attempt() (+27 more)

### Community 6 - "Test Prompt Builder"
Cohesion: 0.08
Nodes (33): build_fallback_prompt(), build_prompt(), build_quiz_prompt(), _default_profile_for_mode(), _learn_instructions(), Centralized prompt template construction and routing., Build a complete prompt for the given learning mode., Build a strict quiz-generation prompt. (+25 more)

### Community 7 - "Question Router"
Cohesion: 0.10
Nodes (30): clean_context_for_llm(), clean_context_text(), Clean PDF-extracted text before sending to the LLM., Normalize textbook chunk text for clearer LLM reading., Trim textbook noise before sending context to the LLM., Keep the most relevant chunks within a character budget for the LLM., trim_context_chunks(), format_retrieved_chunks() (+22 more)

### Community 8 - "App"
Cohesion: 0.12
Nodes (21): Question answering endpoint., Audio generation endpoint., Document listing and detail endpoints., Hindi explanation endpoint., Quiz generation endpoint., Standard API response helpers., Pydantic request/response schemas for API endpoints., Simplified explanation endpoint. (+13 more)

### Community 9 - "RAG Service"
Cohesion: 0.13
Nodes (33): get_llm(), Return singleton LLM client instance., create_quiz(), Generate a multiple-choice quiz from Saksham or uploaded document content., QuizRequest, Request body for POST /quiz., Ask should return answer when context is available., test_ask_with_retrieved_context() (+25 more)

### Community 10 - "BM25 Search"
Cohesion: 0.10
Nodes (20): chapter_storage_key(), ChapterBM25, get_bm25_store(), BM25 lexical index for Saksham curriculum chapters (built at ingest, loaded offl, BM25 search within one chapter., Build serializable BM25 sidecar from FAISS id_map after ingest., Persist BM25 sidecar to disk., Return singleton BM25 store. (+12 more)

### Community 11 - "Embeddings"
Cohesion: 0.11
Nodes (22): embed_batch(), embed_text(), EmbeddingModel, get_embedding_model(), MockEmbeddings, preload_embedding_model(), Embedding generation using multilingual-e5-small., Deterministic mock embeddings for testing. (+14 more)

### Community 12 - "Conftest"
Cohesion: 0.12
Nodes (26): MockLLM, Deterministic mock LLM for testing., FaissManager, Session, BaseSettings, Central configuration for Saksham AI backend., Return database URL with absolute path for SQLite., Settings (+18 more)

### Community 13 - "Curriculum Utils"
Cohesion: 0.11
Nodes (27): Path, chapter_matches(), ChapterInfo, discover_chapter_pdfs(), normalize_subject(), Utilities for Saksham curriculum PDF discovery and naming., Metadata for a curriculum chapter PDF., Convert text to a URL-safe chapter identifier. (+19 more)

### Community 14 - "Reranker"
Cohesion: 0.11
Nodes (17): LLMClient, Protocol for LLM client implementations., Generate text from a prompt., CrossEncoderReranker, get_reranker(), NoOpReranker, Optional cross-encoder reranker for Saksham retrieval (lazy-loaded, Jetson-safe), Passthrough when reranking is disabled. (+9 more)

### Community 15 - "Knowledge Service"
Cohesion: 0.10
Nodes (23): compute_curriculum_hash(), list_chapters(), list_classes(), list_subjects(), list_topics(), _manifest_chapters(), Return chapters from manifest, or discover PDFs if manifest empty., Return available class levels from curriculum manifest. (+15 more)

### Community 16 - "  Init  "
Cohesion: 0.11
Nodes (13): FAISS vector index management., Reset saksham index singleton (for rebuild)., reset_saksham_index(), Ollama LLM client for local inference., Configuration package., Application settings loaded from environment variables., Document indexing into FAISS., Document processing package. (+5 more)

### Community 17 - "Llm"
Cohesion: 0.14
Nodes (19): OllamaLLM, Production LLM client using Ollama HTTP API., Send prompt to Ollama and return generated text., Check if Ollama service is reachable., hindi_explanation(), Generate Hindi explanation for a question., LearningModeRequest, Shared request for simplify and hindi endpoints. (+11 more)

### Community 18 - "Quiz Generation"
Cohesion: 0.11
Nodes (21): Override LLM client (for testing)., set_llm(), parse_quiz_response(), _parse_quiz_text_lines(), parse_quiz_text_response(), Parse MCQ blocks line-by-line, including inline Answer markers., Parse plain-text MCQ blocks from LLM output., Parse quiz output from LLM response (plain text first, JSON fallback). (+13 more)

### Community 19 - "Exceptions"
Cohesion: 0.11
Nodes (20): Request body for POST /summary., SummaryRequest, generate_summary(), Get or regenerate document summary., Upload and process a PDF document., upload_document(), Session, Session (+12 more)

### Community 20 - "Saksham"
Cohesion: 0.14
Nodes (20): get_document(), list_documents(), Return list of uploaded documents., Return document details including stored quizzes., error_response(), Return a standardized error JSON response., Return a standardized success JSON response., success_response() (+12 more)

### Community 21 - "Download Models"
Cohesion: 0.18
Nodes (19): Path, get_settings(), Return cached settings instance., Create required data directories if they do not exist., Namespace, BundledModel, cleanup_bundled_models(), _cleanup_model_dir() (+11 more)

### Community 22 - "Quiz Generation"
Cohesion: 0.17
Nodes (17): Any, Path, _cache_dir(), _cache_key(), cache_path(), load_cached_quiz(), File-based quiz cache for stateless clients (no login/signup)., Return the JSON cache file path for a quiz request. (+9 more)

### Community 23 - "Chunker"
Cohesion: 0.17
Nodes (16): _count_tokens(), create_chunks(), create_curriculum_chunks(), Token-based text chunking using word approximation., Chunk NCERT PDF text by section first, then by token size.      Keeps related pa, Truncate text to a maximum approximate token count., Split text into words., Approximate token count from word count. (+8 more)

### Community 24 - "Quiz Generation"
Cohesion: 0.16
Nodes (16): filter_quiz_source_chunks(), is_exercise_list_chunk(), _join_context_chunks(), prepare_quiz_context(), Prepare chapter/document text for quiz generation., Detect end-of-chapter exercise blocks that make poor quiz sources., Drop low-quality and exercise-list chunks before quiz generation., Evenly sample chunks when the full chapter exceeds the context budget. (+8 more)

### Community 25 - "Test Accessibility Service"
Cohesion: 0.15
Nodes (14): AccessibilityProfile, LearningMode, Accessibility profile to prompt mode mapping., Resolve the effective learning mode based on accessibility profile.      Accessi, resolve_mode(), Unit tests for accessibility service., Beginner profile should override to BEGINNER mode., Dyslexia profile should override to DYSLEXIA mode. (+6 more)

### Community 26 - "Retrieval Pipeline"
Cohesion: 0.16
Nodes (16): get_saksham_index(), Return singleton Saksham knowledge base FAISS index., ChunkContext, _get_chapter_chunk_texts(), _hybrid_retrieve_chapter(), _prepend_phrase_matched_chunks(), Retrieved chunk with metadata., Prepend chunks that contain the most specific question phrases. (+8 more)

### Community 27 - "Retrieval Pipeline"
Cohesion: 0.17
Nodes (15): _extract_focused_snippet(), _extract_profile_snippet(), _find_passage_end(), _is_strong_keyword_match(), _merge_semantic_and_keyword_contexts(), _parse_activity_ref(), _profile_start(), RAG retrieval service for document and Saksham knowledge base. (+7 more)

### Community 28 - "Bio Formatter"
Cohesion: 0.17
Nodes (13): is_bio_question(), _profile_start(), Deterministic answers for textbook biography and sidebar profiles., Pick the sidebar header closest before the person's name., Return True when the student is asking about a person, not an event or concept., Extract a biography sidebar (e.g. 'Be a scientist') when the context contains it, try_format_bio_answer(), extract_query_terms() (+5 more)

### Community 29 - "Constants"
Cohesion: 0.19
Nodes (14): AskResponse, AudioRequest, Response data for POST /ask., Request body for POST /audio., BaseModel, AccessibilityProfile, AnswerProfile, IndexName (+6 more)

### Community 30 - "Test Content Refs"
Cohesion: 0.16
Nodes (13): extract_content_refs(), Extract textbook activity/figure/section references from a question., Unit tests for textbook reference extraction and retrieval boosting., Should extract activity references from questions., Should extract figure references from questions., Activity references should outrank bare section numbers., Snippet extraction should center on the referenced activity., Who-was questions should yield the person's name. (+5 more)

### Community 31 - "Test Upload Flow"
Cohesion: 0.18
Nodes (9): SQLAlchemy ORM models., Repository pattern for database access., _make_pdf_bytes(), Integration tests for upload flow., Upload PDF then query it via /ask., Upload should store summary and quiz retrievable via endpoints., test_upload_summary_quiz(), test_upload_to_query_flow() (+1 more)

### Community 32 - "Processor"
Cohesion: 0.18
Nodes (13): Session, PDFProcessingError, Raised when PDF extraction or validation fails., _clean_text(), extract_text(), Normalize whitespace in extracted text., Extract text from a PDF file.      Returns:         Tuple of (cleaned_text, page, _normalize_questions() (+5 more)

### Community 33 - "Repositories"
Cohesion: 0.19
Nodes (9): Chunk, Text chunk linked to a document and FAISS vector., QuizRepository, Data access for quiz questions., Store multiple quiz questions for a document., Fetch all quiz questions for a document., Remove all quiz questions for a document., Serialize quiz records to dictionaries. (+1 more)

### Community 34 - "Test Answer Formatter"
Cohesion: 0.20
Nodes (10): format_student_answer(), Post-process LLM answers for student-facing clarity and safety., Strip chatbot filler and fix common formatting issues in LLM output., Unit tests for answer and context formatting., Meta phrases about the student or context should be removed., PDF bullet markers should become readable list items., Chatbot greetings and closings should be removed., test_clean_context_text_normalizes_pdf_bullets() (+2 more)

### Community 35 - "Test Upload Api"
Cohesion: 0.20
Nodes (11): _make_pdf_bytes(), API tests for upload endpoint., Create PDF bytes for testing., Non-PDF files should be rejected., Empty files should be rejected., Valid PDF upload should return document metadata., Integration test with real Ollama (skipped by default)., test_upload_integration_real_llm() (+3 more)

### Community 36 - "Embeddings"
Cohesion: 0.27
Nodes (5): Generate embeddings for a batch of texts., Production embedding model using sentence-transformers., Resolve model to a local directory path for offline-safe loading., Generate embedding for a single text., SentenceTransformerEmbeddings

### Community 37 - "Retrieval Pipeline"
Cohesion: 0.20
Nodes (10): _extract_content_phrases(), get_search_terms(), _keyword_match_score(), Extract multi-word phrases from a question for focused chapter retrieval., Merge textbook references with named-entity and content phrases for retrieval., Score how strongly a chunk matches explicit textbook references or phrases., test_keyword_match_score_prefers_full_name(), Unit tests for retrieval helpers. (+2 more)

### Community 38 - "Repositories"
Cohesion: 0.20
Nodes (7): Any, Session, Document, Quiz, Uploaded document metadata., Multiple-choice quiz question for a document., Serialize document to dictionary.

### Community 39 - "Test Saksham Retrieval"
Cohesion: 0.20
Nodes (9): Clear cached BM25 store (tests)., reset_bm25_store_for_testing(), Reset singleton indexes (for testing)., reset_indexes_for_testing(), Clear cached reranker (tests)., reset_reranker_for_testing(), Unit tests for Saksham chapter-scoped retrieval., Retrieval should return chunks scoped to the selected chapter. (+1 more)

### Community 40 - "Retrieval Pipeline"
Cohesion: 0.20
Nodes (10): _extract_activity_passage(), _find_best_activity_start(), _merge_chunk_text(), Append the next chunk, removing duplicated overlap from PDF chunking., Prefer real activity headers over broken PDF fragment matches., Return the chunk index and offset of the best activity header match., Extract the full text of one activity across overlapping PDF chunks., _score_activity_header() (+2 more)

### Community 41 - "Test Pdf Parser"
Cohesion: 0.22
Nodes (9): _create_test_pdf(), Unit tests for PDF parser., Create a temporary PDF with given text., Valid PDF should return extracted text., PDF with no text should raise PDFProcessingError., Invalid file should raise PDFProcessingError., test_extract_text_corrupted_file(), test_extract_text_empty_pdf() (+1 more)

### Community 42 - "Hybrid Search"
Cohesion: 0.25
Nodes (7): merge_ranked_lists(), Hybrid retrieval utilities: reciprocal rank fusion and candidate merging., Merge multiple ranked faiss_id lists using Reciprocal Rank Fusion.      Returns, Interleave two ranked lists without duplicates up to limit., reciprocal_rank_fusion(), Unit tests for hybrid RRF merging., test_reciprocal_rank_fusion_prefers_shared_hits()

### Community 43 - "Repositories"
Cohesion: 0.25
Nodes (5): Create a new document record., Fetch a document by primary key., Return all documents ordered by upload date descending., Update summary and key concepts after auto-analysis., Document

### Community 44 - "Retrieval Pipeline"
Cohesion: 0.25
Nodes (8): _augment_contexts_with_chapter_intro(), _get_ordered_chapter_chunks(), _is_low_quality_chunk(), Filter page footers and near-empty chunks that pollute semantic search., Return (chunk_index, text, faiss_id) tuples sorted by chunk_index., Prepend early chapter chunks so broad questions include causes and background., Page footers with dot leaders should be filtered., test_is_low_quality_chunk_footer()

### Community 45 - "Test Ask Api"
Cohesion: 0.25
Nodes (7): API tests for ask endpoint., Empty question should return 422., Non-existent document_id should return 404., Saksham source without class/subject/chapter should return 422., test_ask_document_not_found(), test_ask_empty_question(), test_ask_saksham_missing_params()

### Community 46 - "Test Documents Api"
Cohesion: 0.25
Nodes (7): API tests for document endpoints., Missing document should return 404., Existing document should return details with quizzes., Empty document list should return success., test_get_document_not_found(), test_get_document_success(), test_list_documents_empty()

### Community 47 - "Quiz Generation"
Cohesion: 0.25
Nodes (7): API tests for quiz generation., Document quiz should require document_id., Saksham quiz should return normalized MCQs., Saksham quiz should validate required chapter fields., test_document_quiz_requires_document_id(), test_saksham_quiz_requires_chapter_fields(), test_saksham_quiz_returns_questions()

### Community 48 - "Test Learning Modes"
Cohesion: 0.25
Nodes (7): Integration tests for learning modes., Hindi endpoint should return Hindi answer., Health endpoint should return healthy status., Simplify endpoint should return simplified answer., test_health_check(), test_hindi_mode(), test_simplify_mode()

### Community 49 - "Test Repositories"
Cohesion: 0.25
Nodes (7): Unit tests for database repositories., Chunk repository should store and retrieve chunks., Quiz repository should store and retrieve quizzes., Document repository should create and retrieve documents., test_chunk_repository(), test_document_repository_crud(), test_quiz_repository()

### Community 50 - "Retrieval Pipeline"
Cohesion: 0.33
Nodes (7): _get_ordered_document_chunks(), _has_strong_keyword_match(), Return True when keyword matches are specific enough to skip semantic noise., Return (chunk_index, text, faiss_id) for a uploaded document., Retrieve relevant chunks from user document index., retrieve_document_context(), Session

### Community 51 - "Audio Service"
Cohesion: 0.29
Nodes (6): create_audio(), Convert text to speech using Piper TTS., AudioRequest, generate_audio(), Text-to-speech service using Piper TTS., Convert text to speech using Piper TTS.      Returns:         Dict with audio_pa

### Community 52 - "Repositories"
Cohesion: 0.29
Nodes (4): Chunk, Fetch chunks by FAISS vector IDs., Fetch all chunks for a document., Create multiple chunks. Each tuple is (chunk_index, chunk_text, faiss_id).

### Community 53 - "API Endpoints"
Cohesion: 0.40
Nodes (6): ask_question(), Answer a question using RAG., AskRequest, Request body for POST /ask., AskRequest, Session

### Community 54 - "Test Rag Saksham"
Cohesion: 0.33
Nodes (5): Integration tests for Saksham knowledge base., Chapters endpoint should return Class 8 Science chapters., Ask with saksham source should return an answer from chapter content., test_saksham_ask(), test_saksham_chapters_api()

### Community 55 - "Seed Kb"
Cohesion: 0.40
Nodes (5): get_content(), main(), Generate Saksham knowledge base seed topic files., Return content for a topic, using class-specific or default content., Generate all 50 topic JSON files.

### Community 56 - "Llm"
Cohesion: 0.40
Nodes (3): generate_answer(), Return mock response based on prompt content., Generate text using the default LLM client.

### Community 57 - "Ingest Curriculum"
Cohesion: 0.50
Nodes (3): main(), Ingest curriculum PDFs into Saksham FAISS index., Build Saksham index from curriculum PDFs.

### Community 58 - "Knowledge Service"
Cohesion: 0.50
Nodes (4): get_chapter_from_manifest(), Find chapter metadata by id or title., Slugified ref must match the chapter, not every chapter in the class., test_get_chapter_from_manifest_does_not_match_unrelated_chapters()

### Community 59 - "Db"
Cohesion: 0.67
Nodes (3): Session, get_db(), FastAPI dependency that yields a database session.

## Knowledge Gaps
- **3 isolated node(s):** `version`, `chapters`, `Namespace`
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `answer_question()` connect `RAG Service` to `Activity Formatting`, `Test Answer Formatter`, `Test Prompt Builder`, `Question Router`, `App`, `Llm`, `Retrieval Pipeline`, `API Endpoints`, `Test Accessibility Service`, `Retrieval Pipeline`, `Bio Formatter`, `Test Content Refs`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Why does `DocumentRepository` connect `RAG Service` to `Processor`, `Repositories`, `Quiz Generation`, `Repositories`, `Repositories`, `Test Documents Api`, `Test Repositories`, `Saksham`, `Quiz Generation`, `Test Upload Flow`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `ValidationError` connect `RAG Service` to `Knowledge Service`, `Quiz Generation`, `Llm`, `Exceptions`, `Audio Service`, `API Endpoints`, `Quiz Generation`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `answer_question()` (e.g. with `DocumentNotFoundError` and `ValidationError`) actually correct?**
  _`answer_question()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `ValidationError` (e.g. with `AskRequest` and `AudioRequest`) actually correct?**
  _`ValidationError` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `DocumentRepository` (e.g. with `Session` and `Session`) actually correct?**
  _`DocumentRepository` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `FaissManager` (e.g. with `Any` and `FaissManager`) actually correct?**
  _`FaissManager` has 14 INFERRED edges - model-reasoned connections that need verification._