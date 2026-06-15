# Graph Report - backend  (2026-06-14)

## Corpus Check
- 134 files · ~4,323,418 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1604 nodes · 3822 edges · 74 communities (69 shown, 5 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 318 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `53507a55`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 77|Community 77]]

## God Nodes (most connected - your core abstractions)
1. `ValidationError` - 65 edges
2. `DocumentRepository` - 56 edges
3. `ServiceUnavailableError` - 46 edges
4. `get_settings()` - 43 edges
5. `DocumentNotFoundError` - 42 edges
6. `AccessibilityProfile` - 41 edges
7. `ChunkRepository` - 41 edges
8. `answer_question()` - 39 edges
9. `FaissManager` - 36 edges
10. `LearningMode` - 35 edges

## Surprising Connections (you probably didn't know these)
- `Any` --uses--> `FaissManager`  [INFERRED]
  documents/indexer.py → ai/faiss_manager.py
- `FaissManager` --uses--> `FaissManager`  [INFERRED]
  documents/indexer.py → ai/faiss_manager.py
- `LocalizeContentType` --uses--> `LocalizeContentType`  [INFERRED]
  ai/hindi_localize_prompt.py → config/constants.py
- `Client` --uses--> `ServiceUnavailableError`  [INFERRED]
  ai/llm.py → exceptions.py
- `Any` --uses--> `AccessibilityProfile`  [INFERRED]
  api/accessibility_helpers.py → config/constants.py

## Import Cycles
- 1-file cycle: `app.py -> app.py`
- 2-file cycle: `api/saksham.py -> app.py -> api/saksham.py`
- 2-file cycle: `api/ask.py -> app.py -> api/ask.py`
- 2-file cycle: `api/audio.py -> app.py -> api/audio.py`
- 2-file cycle: `api/documents.py -> app.py -> api/documents.py`
- 2-file cycle: `api/hindi.py -> app.py -> api/hindi.py`
- 2-file cycle: `api/localize.py -> app.py -> api/localize.py`
- 2-file cycle: `api/quiz.py -> app.py -> api/quiz.py`
- 2-file cycle: `api/simplify.py -> app.py -> api/simplify.py`
- 2-file cycle: `api/summary.py -> app.py -> api/summary.py`
- 2-file cycle: `api/upload.py -> app.py -> api/upload.py`

## Communities (74 total, 5 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.16
Nodes (23): QuestionSourceType, _attach_meta(), _build_mcq(), _candidate_phrases(), _chunk_windows(), _collect_phrase_pool(), extract_list_questions(), extract_sentence_cloze_questions() (+15 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (48): build_pointwise_speech_lines(), _chunk_bullets(), extract_preserve_terms(), extract_speech_points(), format_dyslexia_text(), prepare_segment_for_speech(), Deterministic dyslexia-friendly text formatting (no LLM)., Return bullet/sentence segments for read-along highlighting. (+40 more)

### Community 2 - "Community 2"
Cohesion: 0.19
Nodes (15): parse_quiz_question_json(), Any, Validation helpers for Hinenglish localization output., Return (ok, reason) for Hinenglish prose output., Parse LLM JSON for one translated quiz question., Ensure translated quiz question preserves structure., validate_prose_hindi(), validate_quiz_payload() (+7 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (30): build_summary_expand_prompt(), Ask the LLM to expand a short draft using the source context., API tests for summary generation., test_saksham_summary_returns_prose_payload(), clean_summary_text(), count_paragraphs(), count_words(), _dedupe_paragraphs() (+22 more)

### Community 4 - "Community 4"
Cohesion: 0.16
Nodes (18): ActivityIntent, Which part of an activity the student is asking about., format_student_answer(), Post-process LLM answers for student-facing clarity and safety., Strip chatbot filler and fix common formatting issues in LLM output., AnswerProfile, How tightly the LLM must stick to retrieved textbook text., answer_question() (+10 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (24): AccessibilityProfile, Any, Helper to enrich API responses with accessibility metadata., with_accessibility(), Question answering endpoint., Audio generation endpoint., Document listing and detail endpoints., Hindi explanation endpoint (deprecated — use English endpoints + POST /localize/ (+16 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (49): _action_before_questions(), _clean_step_text(), _dedupe_procedure_steps(), detect_activity_intent(), _extract_activity_explanation(), _extract_aim(), _extract_bullet_steps(), _extract_conclusion() (+41 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (48): AskRequest, AskResponse, AudioRequest, LearningModeRequest, LocalizeHiRequest, QuizLocalizePayload, QuizQuestionLocalize, QuizRequest (+40 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (41): Load and query pre-built BM25 indexes per chapter., SakshamBM25Store, Persist Saksham index to disk., Reset saksham index singleton (for rebuild)., reset_saksham_index(), save_saksham_index(), ChapterInfo, main() (+33 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (50): clean_context_for_llm(), clean_context_text(), Clean PDF-extracted text before sending to the LLM., Normalize textbook chunk text for clearer LLM reading., Trim textbook noise before sending context to the LLM., filter_quiz_source_chunks(), is_exercise_list_chunk(), _join_context_chunks() (+42 more)

### Community 10 - "Community 10"
Cohesion: 0.15
Nodes (30): ask_question(), Session, Answer a question using RAG., LearningModeRequest, Session, create_quiz(), Session, Quiz generation endpoint. (+22 more)

### Community 11 - "Community 11"
Cohesion: 0.06
Nodes (45): _count_tokens(), create_chunks(), create_curriculum_chunks(), Token-based text chunking using word approximation., Chunk NCERT PDF text by section first, then by token size.      Keeps related pa, Truncate text to a maximum approximate token count., Split text into words., Approximate token count from word count. (+37 more)

### Community 12 - "Community 12"
Cohesion: 0.10
Nodes (29): build_fallback_prompt(), build_prompt(), build_quiz_prompt(), _default_profile_for_mode(), _learn_instructions(), AnswerProfile, LearningMode, Centralized prompt template construction and routing. (+21 more)

### Community 13 - "Community 13"
Cohesion: 0.33
Nodes (5): Integration tests for Saksham knowledge base., Chapters endpoint should return Class 8 Science chapters., Ask with saksham source should return an answer from chapter content., test_saksham_ask(), test_saksham_chapters_api()

### Community 14 - "Community 14"
Cohesion: 0.04
Nodes (48): 10. POST /simplify — simplified answers, 11. POST /upload — user PDF pipeline, 12. Document management, 13. POST /audio — standalone TTS, 14. Accessibility profiles (dyslexia, beginner, visual), 15. POST /localize/hi — Hinenglish conversion, 16. POST /hindi — deprecated, 17. Edge / PDF-free deployment check (+40 more)

### Community 15 - "Community 15"
Cohesion: 0.10
Nodes (33): chapter_matches(), discover_chapter_pdfs(), normalize_subject(), Path, Utilities for Saksham curriculum PDF discovery and naming., Discover chapter PDFs under class{N}/{subject}/*.pdf layout., Convert text to a URL-safe chapter identifier., Convert folder name to display subject (e.g. science -> Science). (+25 more)

### Community 16 - "Community 16"
Cohesion: 0.05
Nodes (78): get_chapter_chunk_texts(), Return all chunk texts for a chapter from FAISS metadata (direct lookup)., Validate chapter exists in manifest and index., validate_saksham_chapter(), _cache_dir(), _cache_key(), cache_path(), load_cached_quiz() (+70 more)

### Community 17 - "Community 17"
Cohesion: 0.10
Nodes (24): Chunk, Base, Chunk, Document, Quiz, SQLAlchemy ORM models., Base class for all ORM models., Uploaded document metadata. (+16 more)

### Community 18 - "Community 18"
Cohesion: 0.08
Nodes (50): _approx_equal(), build_chapter_quiz_questions(), build_concept_questions(), build_definition_questions(), build_fact_questions(), build_triangle_inequality_questions(), detect_math_chapter_kind(), _deterministic_shuffle() (+42 more)

### Community 19 - "Community 19"
Cohesion: 0.09
Nodes (37): Clear cached BM25 store (tests)., reset_bm25_store_for_testing(), get_user_index(), FAISS vector index management., Return singleton user document FAISS index., Persist user index to disk., Replace the user index with a fresh empty index and persist it., Reset singleton indexes (for testing). (+29 more)

### Community 20 - "Community 20"
Cohesion: 0.06
Nodes (31): 1. Discover chapters, 2. Staleness check, 3. PDF → text, 4. Section-aware chunking (Phase 1), 5. Embed and index, 6. BM25 sidecar (Phase 1), 7. Save manifest, Ask pipeline (`POST /ask`) (+23 more)

### Community 21 - "Community 21"
Cohesion: 0.14
Nodes (14): _extract_activity_passage(), _find_best_activity_start(), _find_passage_end(), _merge_chunk_text(), _parse_activity_ref(), Append the next chunk, removing duplicated overlap from PDF chunking., Parse 'Activity 6.2' into (chapter, section) numbers., Find where the current activity passage should end inside a text block. (+6 more)

### Community 22 - "Community 22"
Cohesion: 0.11
Nodes (22): Clear cached embedding model so the next call loads the real/default model., reset_embedding_model_for_testing(), MockLLM, Deterministic mock LLM for testing., Return mock response based on prompt content., FixtureRequest, MonkeyPatch, TestClient (+14 more)

### Community 23 - "Community 23"
Cohesion: 0.12
Nodes (15): FaissManager, Any, ndarray, Path, Search only vectors whose metadata passes filter_fn., Persist index and metadata to disk., Load index and metadata from disk. Returns True if successful., Return number of vectors in the index. (+7 more)

### Community 24 - "Community 24"
Cohesion: 0.17
Nodes (24): prepare_segment_for_speech(), Normalize one Hindi segment for TTS., AudioLanguage, generate_audio(), _generate_with_binary(), _generate_with_python(), _load_piper_voice(), _pointwise_speech_lines() (+16 more)

### Community 25 - "Community 25"
Cohesion: 0.11
Nodes (15): chapter_storage_key(), ChapterBM25, Any, BM25 search within one chapter., Build serializable BM25 sidecar from FAISS id_map after ingest., Persist BM25 sidecar to disk., Stable key for a chapter in the BM25 sidecar file., Tokenize text for BM25 (lowercase alphanumeric tokens). (+7 more)

### Community 26 - "Community 26"
Cohesion: 0.15
Nodes (20): ChunkRepository, Data access for document chunks., Create multiple chunks. Each tuple is (chunk_index, chunk_text, faiss_id)., Fetch chunks by FAISS vector IDs., Fetch all chunks for a document., _apply_accessibility_to_payload(), _build_response_payload(), _document_payload_from_db() (+12 more)

### Community 27 - "Community 27"
Cohesion: 0.29
Nodes (7): _prebuilt_index_available(), Return True if a pre-built Saksham index and manifest exist on disk., Tests for pre-built index loading without source PDFs., Server startup should load index even when curriculum PDFs are removed., Pre-built index files should exist after curriculum ingest., test_prebuilt_index_available(), test_startup_without_pdfs()

### Community 28 - "Community 28"
Cohesion: 0.16
Nodes (18): build_hindi_pointwise_speech_lines(), devanagari_char_count(), devanagari_ratio(), extract_preserve_terms_from_english(), extract_speech_points(), Hindi text formatting helpers for localization output., Return ratio of Devanagari chars to all non-whitespace chars., Collect Latin tokens from English source text worth preserving in Hinenglish. (+10 more)

### Community 29 - "Community 29"
Cohesion: 0.17
Nodes (19): BaseSettings, Central configuration for Saksham AI backend., Return database URL with absolute path for SQLite., Settings, purge_cache_dir_if_version_changed(), purge_caches_on_version_change(), Path, Settings (+11 more)

### Community 30 - "Community 30"
Cohesion: 0.22
Nodes (8): CrossEncoderReranker, NoOpReranker, Optional cross-encoder reranker for Saksham retrieval (lazy-loaded, Jetson-safe), Passthrough when reranking is disabled., Lazy-loaded sentence-transformers CrossEncoder reranker., Unit tests for optional cross-encoder reranker., test_cross_encoder_falls_back_when_model_unavailable(), test_noop_reranker_passthrough()

### Community 31 - "Community 31"
Cohesion: 0.15
Nodes (18): is_valid_grounded_question(), Reject malformed or low-quality grounded MCQs., build_science_concept_questions(), extract_science_definition_questions(), filter_science_questions(), is_science_subject(), is_valid_science_question(), Any (+10 more)

### Community 32 - "Community 32"
Cohesion: 0.19
Nodes (14): get_settings(), Application settings loaded from environment variables., Create required data directories if they do not exist., Return cached settings instance., init_db(), Create all database tables., _download_files(), download_piper_hindi_voice() (+6 more)

### Community 33 - "Community 33"
Cohesion: 0.16
Nodes (16): is_bio_question(), _profile_start(), Deterministic answers for textbook biography and sidebar profiles., Pick the sidebar header closest before the person's name., Return True when the student is asking about a person, not an event or concept., Extract a biography sidebar (e.g. 'Be a scientist') when the context contains it, try_format_bio_answer(), extract_query_terms() (+8 more)

### Community 34 - "Community 34"
Cohesion: 0.13
Nodes (16): _extract_focused_snippet(), _extract_profile_snippet(), _keyword_match_score(), _profile_start(), Pick the sidebar header closest before the person's name., Extract a textbook sidebar profile around a person's name., Extract text around the strongest reference match inside one chunk., Score how strongly a chunk matches explicit textbook references or phrases. (+8 more)

### Community 35 - "Community 35"
Cohesion: 0.25
Nodes (16): Namespace, BundledModel, cleanup_bundled_models(), _cleanup_model_dir(), _download_model(), main(), _model_is_complete(), _print_env_snippet() (+8 more)

### Community 36 - "Community 36"
Cohesion: 0.23
Nodes (14): build_grounded_chapter_questions(), _collect_list_items(), extract_definition_questions(), filter_grounded_questions(), Build MCQs from definition-style sentences in chapter text., Verify a grounded MCQ against chapter source text., Keep only verified grounded MCQs., Build factual MCQs from chapter text using tiered, verified extractors.      Pri (+6 more)

### Community 37 - "Community 37"
Cohesion: 0.29
Nodes (6): get_reranker(), Return configured reranker singleton., Protocol for reranking candidate passages., Return (faiss_id, score, text) sorted by relevance., Reranker, Protocol

### Community 38 - "Community 38"
Cohesion: 0.15
Nodes (12): Browser demo, Dyslexia Mode — Testing Guide, Expected response shape (when dyslexia profile is set), POST /ask (document + dyslexia + audio), POST /ask (Saksham + dyslexia), POST /audio (standalone TTS), POST /hindi (dyslexia — Hindi LLM + bullet formatter), POST /quiz (Saksham + dyslexia) (+4 more)

### Community 39 - "Community 39"
Cohesion: 0.11
Nodes (36): embed_text(), Embed a single text using the default model., get_saksham_index(), Return singleton Saksham knowledge base FAISS index., _augment_contexts_with_chapter_intro(), ChunkContext, _get_chapter_chunk_texts(), _get_ordered_chapter_chunks() (+28 more)

### Community 40 - "Community 40"
Cohesion: 0.17
Nodes (11): API tests for document endpoints., Missing document should return 404., Existing document should return details with quizzes., Deleting a missing document should return 404., Deleting a document should remove its stored PDF file., Empty document list should return success., test_delete_document_not_found(), test_delete_document_success() (+3 more)

### Community 41 - "Community 41"
Cohesion: 0.20
Nodes (11): _make_pdf_bytes(), API tests for upload endpoint., Create PDF bytes for testing., Non-PDF files should be rejected., Empty files should be rejected., Valid PDF upload should return document metadata., Integration test with real Ollama (skipped by default)., test_upload_integration_real_llm() (+3 more)

### Community 42 - "Community 42"
Cohesion: 0.27
Nodes (5): Generate embeddings for a batch of texts., Production embedding model using sentence-transformers., Resolve model to a local directory path for offline-safe loading., Generate embedding for a single text., SentenceTransformerEmbeddings

### Community 43 - "Community 43"
Cohesion: 0.18
Nodes (10): Answer or summary (prose), content_type values, Deprecated: POST /hindi, Flow, Hindi audio setup, Hinenglish Localization — Backend Guide, Hinenglish rules, POST /localize/hi (+2 more)

### Community 45 - "Community 45"
Cohesion: 0.28
Nodes (7): merge_ranked_lists(), Hybrid retrieval utilities: reciprocal rank fusion and candidate merging., Merge multiple ranked faiss_id lists using Reciprocal Rank Fusion.      Returns, Interleave two ranked lists without duplicates up to limit., reciprocal_rank_fusion(), Unit tests for hybrid RRF merging., test_reciprocal_rank_fusion_prefers_shared_hits()

### Community 46 - "Community 46"
Cohesion: 0.28
Nodes (8): FaissManager, Unit tests for FAISS manager., Empty index should return no results., Index should persist and reload correctly., Adding vectors and searching should return results., test_create_and_search(), test_save_and_load_index(), test_search_empty_index()

### Community 47 - "Community 47"
Cohesion: 0.32
Nodes (7): _extract_content_phrases(), get_search_terms(), Extract multi-word phrases from a question for focused chapter retrieval., Merge textbook references with named-entity and content phrases for retrieval., Unit tests for retrieval helpers., test_search_terms_include_content_phrases_for_electricity_question(), test_search_terms_include_minimum_wages_phrase()

### Community 48 - "Community 48"
Cohesion: 0.25
Nodes (7): API tests for quiz generation., Document quiz should require document_id., Saksham quiz should return normalized MCQs., Saksham quiz should validate required chapter fields., test_document_quiz_requires_document_id(), test_saksham_quiz_requires_chapter_fields(), test_saksham_quiz_returns_questions()

### Community 49 - "Community 49"
Cohesion: 0.25
Nodes (7): Integration tests for learning modes., Hindi endpoint should return Hindi answer., Health endpoint should return healthy status., Simplify endpoint should return simplified answer., test_health_check(), test_hindi_mode(), test_simplify_mode()

### Community 51 - "Community 51"
Cohesion: 0.25
Nodes (7): Unit tests for database repositories., Chunk repository should store and retrieve chunks., Quiz repository should store and retrieve quizzes., Document repository should create and retrieve documents., test_chunk_repository(), test_document_repository_crud(), test_quiz_repository()

### Community 52 - "Community 52"
Cohesion: 0.29
Nodes (6): End-to-end flowchart, Key files, Key settings (`.env`), Response shape, Summary Generation Flow, Upload vs Saksham (what is identical)

### Community 53 - "Community 53"
Cohesion: 0.38
Nodes (6): _make_pdf_bytes(), Integration tests for upload flow., Upload PDF then query it via /ask., Upload should store summary and quiz retrievable via endpoints., test_upload_summary_quiz(), test_upload_to_query_flow()

### Community 56 - "Community 56"
Cohesion: 0.33
Nodes (3): Fetch a document by primary key., Update summary and key concepts after auto-analysis., Delete a document record. Related chunks and quizzes cascade.

### Community 57 - "Community 57"
Cohesion: 0.40
Nodes (5): get_content(), main(), Generate Saksham knowledge base seed topic files., Return content for a topic, using class-specific or default content., Generate all 50 topic JSON files.

### Community 58 - "Community 58"
Cohesion: 0.18
Nodes (19): build_summary_prompt(), Build a plain-text chapter/document summary prompt for the local LLM., build_minimal_source_summary(), Build a grounded summary from factual source sentences (no LLM)., build_document_summary_from_chunks(), _finalize_summary(), _generate_from_chunks(), generate_summary_from_chunks() (+11 more)

### Community 62 - "Community 62"
Cohesion: 0.11
Nodes (21): embed_batch(), EmbeddingModel, get_embedding_model(), MockEmbeddings, preload_embedding_model(), ndarray, Embedding generation using multilingual-e5-small., Deterministic mock embeddings for testing. (+13 more)

### Community 63 - "Community 63"
Cohesion: 0.16
Nodes (18): Keep the most relevant chunks within a character budget for the LLM., trim_context_chunks(), format_retrieved_chunks(), Join retrieved chunks into a single context string., context_char_limit(), AnswerProfile, Return the context budget for the given answer profile., Return how many chunks to retrieve for the given answer profile. (+10 more)

### Community 64 - "Community 64"
Cohesion: 0.20
Nodes (14): build_prose_localize_prompt(), build_quiz_question_localize_prompt(), _class_hint(), _preserve_terms_block(), LocalizeContentType, Prompt templates for English-to-Hinenglish localization (no RAG)., Build prompt to convert English answer/summary/simplify text to Hinenglish., Build prompt to translate one MCQ into Hinenglish JSON. (+6 more)

### Community 65 - "Community 65"
Cohesion: 0.26
Nodes (13): _clean_phrase(), _collect_definition_terms(), _is_usable_definition(), _normalize_term(), Collect answer terms from definition-style sentences., build_fallback_summary(), collect_definition_concepts(), extract_section_titles() (+5 more)

### Community 66 - "Community 66"
Cohesion: 0.22
Nodes (15): _normalize_text(), _text_in_corpus(), ground_summary_text(), _has_phrase_overlap(), is_narrative_heavy_chunk(), is_narrative_sentence(), is_summary_sentence_grounded(), Strip textbook narratives and keep summary sentences grounded in source text. (+7 more)

### Community 67 - "Community 67"
Cohesion: 0.15
Nodes (17): is_broad_concept_question(), Route student questions to strict or guided answer generation., Return True for chapter-level or overview questions needing structured answers., Choose strict textbook grounding or guided teaching for LLM generation.      Act, resolve_answer_profile(), extract_content_refs(), Extract textbook activity/figure/section references from a question., Should extract activity references from questions. (+9 more)

### Community 68 - "Community 68"
Cohesion: 0.50
Nodes (3): get_bm25_store(), BM25 lexical index for Saksham curriculum chapters (built at ingest, loaded offl, Return singleton BM25 store.

### Community 69 - "Community 69"
Cohesion: 0.12
Nodes (15): generate_answer(), get_llm(), LLMClient, OllamaLLM, Ollama LLM client for local inference., Protocol for LLM client implementations., Generate text from a prompt., Production LLM client using Ollama HTTP API. (+7 more)

### Community 71 - "Community 71"
Cohesion: 0.24
Nodes (10): _cache_source_for_quiz(), localize_to_hindi(), _maybe_attach_audio(), Any, Convert English content to Hinenglish.      Does not run RAG — only translates p, Unit tests for Hinenglish localization service., test_localize_prose_returns_hindi_text(), test_localize_prose_uses_cache() (+2 more)

### Community 72 - "Community 72"
Cohesion: 0.09
Nodes (33): create_audio(), Convert text to speech using Piper TTS., get_document(), list_documents(), Session, Return list of uploaded documents., Return document details including stored quizzes., Delete an uploaded document, its PDF file, and its search index vectors. (+25 more)

### Community 73 - "Community 73"
Cohesion: 0.39
Nodes (8): _cache_dir(), cache_key(), cache_path(), load_cached_localize(), Any, Path, File-based cache for Hinenglish localization., save_cached_localize()

### Community 74 - "Community 74"
Cohesion: 0.33
Nodes (10): _cache_dir(), _cache_key(), cache_path(), load_cached_summary(), Any, Path, File-based summary cache for Saksham chapters., save_cached_summary() (+2 more)

### Community 77 - "Community 77"
Cohesion: 0.09
Nodes (32): get_chapters(), get_classes(), get_subjects(), get_topics(), Saksham knowledge base browse endpoints., List available class levels., List subjects for a class level., List curriculum chapters for a class and subject. (+24 more)

## Knowledge Gaps
- **95 isolated node(s):** `Any`, `version`, `chapters`, `Namespace`, `Any` (+90 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `Community 32` to `Community 1`, `Community 3`, `Community 4`, `Community 5`, `Community 7`, `Community 8`, `Community 9`, `Community 11`, `Community 16`, `Community 19`, `Community 22`, `Community 24`, `Community 29`, `Community 30`, `Community 35`, `Community 39`, `Community 58`, `Community 62`, `Community 63`, `Community 64`, `Community 65`, `Community 68`, `Community 69`, `Community 73`, `Community 74`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `ValidationError` connect `Community 10` to `Community 64`, `Community 26`, `Community 4`, `Community 5`, `Community 71`, `Community 72`, `Community 8`, `Community 74`, `Community 11`, `Community 16`, `Community 24`, `Community 58`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `DocumentRepository` connect `Community 19` to `Community 26`, `Community 4`, `Community 5`, `Community 72`, `Community 40`, `Community 10`, `Community 11`, `Community 44`, `Community 16`, `Community 17`, `Community 51`, `Community 53`, `Community 56`, `Community 58`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `ValidationError` (e.g. with `Session` and `LearningModeRequest`) actually correct?**
  _`ValidationError` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `DocumentRepository` (e.g. with `Session` and `Chunk`) actually correct?**
  _`DocumentRepository` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `ServiceUnavailableError` (e.g. with `LLMClient` and `MockLLM`) actually correct?**
  _`ServiceUnavailableError` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `DocumentNotFoundError` (e.g. with `Session` and `Session`) actually correct?**
  _`DocumentNotFoundError` has 25 INFERRED edges - model-reasoned connections that need verification._