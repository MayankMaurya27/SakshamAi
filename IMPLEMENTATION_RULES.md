# IMPLEMENTATION_RULES.md

## Saksham AI Backend Development Rules

### Objective

Build a production-ready, fully offline backend for Saksham AI according to the provided PRD, Backend Technical Specification, and Prompt Specification.

All implementation decisions must prioritize:

* Offline execution
* Edge AI compatibility
* Simplicity
* Maintainability
* Fast development
* Reliability

---

# 1. Core Constraints

The system MUST run completely offline.

Allowed:

* Ollama
* Llama 3.2:1B
* FAISS
* SQLite
* FastAPI
* PyMuPDF
* multilingual-e5-small
* Piper TTS

Forbidden:

* OpenAI API
* Gemini API
* Claude API
* Pinecone
* Weaviate Cloud
* Supabase
* Any external AI service
* Any cloud inference service

---

# 2. Architecture Rules

The implementation MUST follow:

Frontend
→ FastAPI
→ FAISS
→ SQLite
→ Ollama
→ Llama 3.2:1B

Do not introduce unnecessary services.

Do not introduce microservices.

Do not introduce event queues.

Do not introduce distributed systems.

Keep architecture lightweight and suitable for NVIDIA Jetson Orin Nano.

---

# 3. Code Quality Rules

All code must include:

* Type hints
* Docstrings
* Structured logging
* Error handling
* Modular design

Avoid:

* Global variables
* Hardcoded paths
* Duplicated logic
* Monolithic files

---

# 4. Folder Structure Compliance

Follow the Backend Technical Specification exactly.

Do not modify the folder structure unless absolutely necessary.

Keep responsibilities separated:

AI Layer
Document Layer
Database Layer
API Layer
Service Layer

---

# 5. Database Rules

Database:

SQLite

Requirements:

* Use SQLAlchemy ORM
* Create migration-ready schema
* Use repository pattern

Store:

* Documents
* Chunks
* Quizzes
* Metadata

Never store embeddings in SQLite.

Embeddings belong in FAISS only.

---

# 6. FAISS Rules

Maintain two independent indexes:

saksham_index

Contains:

* Educational knowledge base

user_index

Contains:

* Uploaded PDFs
* User documents

Store metadata separately.

FAISS stores vectors only.

---

# 7. PDF Processing Rules

Use:

PyMuPDF

Pipeline:

PDF
→ Extract Text
→ Clean Text
→ Chunk
→ Embed
→ Store

Chunk Size:

700 tokens

Overlap:

100 tokens

Reject:

* Empty PDFs
* Corrupted PDFs

---

# 8. Retrieval Rules

Default Retrieval:

Top K = 5

Retrieval Flow:

Question
→ Embedding
→ FAISS Search
→ Metadata Lookup
→ Prompt Builder
→ LLM

Never send the entire document to the model.

Always use retrieved chunks.

---

# 9. Prompt Rules

Use prompt templates from Prompt Specification.

Never construct prompts dynamically without templates.

Supported Modes:

* Learn
* Simplify
* Hindi
* Quiz
* Summary
* Beginner
* Dyslexia
* Visual Accessibility

Prompt routing must be centralized.

---

# 10. API Rules

All endpoints must:

* Validate input
* Return JSON
* Return proper HTTP status codes
* Return consistent response format

Success Format:

{
"success": true,
"data": {}
}

Error Format:

{
"success": false,
"error": "message"
}

---

# 11. Logging Rules

Use Python logging.

Log:

* Uploads
* Retrieval operations
* LLM calls
* Errors
* Index creation

Never log:

* Full document content
* Sensitive user information

---

# 12. Audio Rules

Use:

Piper TTS

Output:

WAV files

Store in:

data/audio/

Generate audio only when requested.

---

# 13. Learn from Saksham Rules

Educational Knowledge Base format:

JSON

Example:

{
"class": 8,
"subject": "Science",
"topic": "Force",
"content": "..."
}

Do not store educational content as PDFs.

Use structured topic files.

---

# 14. Auto Analysis Rules

Immediately after PDF upload:

Generate:

1. Summary
2. Key Concepts
3. Quiz

Store results in database.

Do not regenerate unless requested.

---

# 15. Performance Rules

Target:

Question Answering:
< 8 seconds

Summary:
< 15 seconds

Quiz:
< 15 seconds

Optimize for Jetson deployment.

---

# 16. Testing Rules

Every module must have tests.

Required Tests:

* PDF Processing
* Embeddings
* FAISS Search
* Retrieval
* Summary Generation
* Quiz Generation
* Hindi Mode
* Learn from Saksham

Do not leave TODO tests.

---

# 17. Security Rules

Validate:

* File types
* File size
* Request payloads

Prevent:

* Path traversal
* Invalid file uploads

Maximum PDF Size:

25 MB

---

# 18. Features Explicitly Excluded From MVP

Do NOT implement:

* Authentication
* User Accounts
* Social Login
* Cloud Storage
* Multi-user Management
* Analytics Dashboard
* Admin Panel
* Docker Orchestration
* Kubernetes
* Payment Systems

Focus only on the MVP.

---

# 19. Definition of Done

Backend is complete only if:

✓ PDF Upload Works

✓ Document Processing Works

✓ FAISS Retrieval Works

✓ Learn from Saksham Works

✓ Summary Generation Works

✓ Quiz Generation Works

✓ Hindi Mode Works

✓ Accessibility Modes Work

✓ Audio Generation Works

✓ Fully Offline Execution Works

✓ Tests Pass

✓ Runs on Jetson-Compatible Environment

No feature is considered complete without successful testing.
