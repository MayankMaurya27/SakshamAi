# Product Requirements Document (PRD)

## Saksham AI – Offline Accessibility & Learning Companion

### Version

v1.0 (MVP)

---

# 1. Product Vision

Saksham AI is an offline, accessibility-first educational learning companion powered by Edge AI, Retrieval-Augmented Generation (RAG), and Small Language Models.

The platform enables students to:

1. Learn from their own documents (PDFs, notes, textbooks)
2. Learn from Saksham's built-in educational knowledge base

while providing:

* Simplified explanations
* Hindi explanations
* Quiz generation
* Summaries
* Audio learning support
* Accessibility-focused learning experiences

All AI processing must run locally without external APIs.

---

# 2. Target Users

Primary Users:

* Class 6–10 Students
* Hindi-speaking learners
* Rural students with limited internet access
* Dyslexic learners
* Visually impaired learners

Secondary Users:

* Teachers
* Parents

---

# 3. Core Product Modules

### Module A: Learn from Document

Users upload:

* PDF
* Notes
* Study Material
* Textbook Chapters

System processes the document and allows interaction through AI learning modes.

---

### Module B: Learn from Saksham

Users select:

* Class
* Subject
* Topic

System retrieves information from Saksham Educational Knowledge Base and generates responses.

---

### Module C: Learning Modes

Supported Modes:

1. Learn Concept
2. Simplify Content
3. Hindi Explain
4. Generate Quiz
5. Summarize Chapter
6. Read Aloud

---

### Module D: Accessibility Profiles

Profiles:

1. Beginner Mode
2. Hindi Learner Mode
3. Dyslexia Support Mode
4. Visual Accessibility Mode

Profiles modify prompts and response formatting.

---

# 4. Functional Requirements

## FR-1 Document Upload

User uploads PDF.

System must:

* Validate file
* Extract text
* Store original PDF
* Generate chunks
* Generate embeddings
* Store vectors
* Store metadata

Accepted Formats:

* PDF

Maximum File Size:

* 25 MB

---

## FR-2 Automatic Document Analysis

After successful upload:

Generate:

* Chapter Summary
* Key Concepts
* Quick Quiz (5 MCQs)

Store generated outputs.

---

## FR-3 Question Answering

User asks:

"What is photosynthesis?"

System:

1. Creates query embedding
2. Retrieves relevant chunks
3. Builds prompt
4. Calls Llama 3.2
5. Returns answer

---

## FR-4 Learn from Saksham

User selects:

Class → Subject → Topic

System retrieves educational content from Saksham Knowledge Base.

No document upload required.

---

## FR-5 Simplify Mode

System rewrites retrieved content using:

* Simpler vocabulary
* Shorter sentences
* Beginner-friendly explanations

---

## FR-6 Hindi Explain Mode

System returns:

* Hindi explanation
* Mixed Hindi-English terminology where appropriate

---

## FR-7 Quiz Generation

Generate:

* 5 MCQs
* Options
* Correct Answer

Based on retrieved context.

---

## FR-8 Summarization

Generate:

* Key points
* Revision notes
* Chapter summary

---

## FR-9 Audio Learning

Convert generated responses into speech.

Output:

* MP3/WAV file
* Playable in frontend

---

# 5. Non-Functional Requirements

### NFR-1 Offline

Must operate without internet.

No external APIs allowed.

---

### NFR-2 Edge AI

Must run on:

NVIDIA Jetson Orin Nano

---

### NFR-3 Latency

Target:

< 8 seconds response time

for normal queries.

---

### NFR-4 Scalability

Support:

* Educational KB
* User Uploaded Documents

using separate vector indexes.

---

# 6. System Architecture

Frontend:

React + Tailwind

Backend:

FastAPI

LLM Runtime:

Ollama

Model:

Llama 3.2 : 1B

Embeddings:

multilingual-e5-small

Vector Search:

FAISS

Metadata Storage:

SQLite

Document Storage:

Local Filesystem

Text-to-Speech:

Piper TTS

---

# 7. Knowledge Architecture

## Index 1

saksham_index

Contains:

* Educational Concepts
* Preloaded Learning Material

Used by:

Learn from Saksham

---

## Index 2

user_index

Contains:

* Uploaded PDFs
* Notes
* Textbooks

Used by:

Learn from Document

---

# 8. Database Schema

Table: documents

Fields:

* id
* filename
* filepath
* upload_date
* summary
* key_concepts

---

Table: chunks

Fields:

* id
* document_id
* chunk_text
* chunk_index

---

Table: quizzes

Fields:

* id
* document_id
* question
* options
* answer

---

# 9. API Endpoints

POST /upload

Upload PDF and process document.

---

POST /ask

Request:

{
"question": "...",
"source": "document | saksham"
}

Response:

{
"answer": "..."
}

---

POST /summary

Generate summary.

---

POST /quiz

Generate quiz.

---

POST /simplify

Generate simplified explanation.

---

POST /hindi

Generate Hindi explanation.

---

GET /documents

Return uploaded document list.

---

GET /document/{id}

Return document details.

---

# 10. RAG Pipeline

Question
↓
Embedding Generation
↓
FAISS Retrieval
↓
Top K Chunks
↓
Prompt Builder
↓
Llama 3.2 : 1B
↓
Response

Top K:

5

Chunk Size:

500–800 tokens

Chunk Overlap:

100 tokens

---

# 11. Prompt Strategy

Learn Mode:

Explain concept clearly using educational language.

---

Simplify Mode:

Explain as if teaching a Class 6 student.

Use examples.

Avoid technical jargon.

---

Hindi Mode:

Explain in Hindi with educational terminology.

---

Quiz Mode:

Generate 5 MCQs from provided context.

---

# 12. Success Criteria

A user can:

1. Upload PDF
2. Receive summary
3. Receive key concepts
4. Ask questions
5. Generate quiz
6. Generate Hindi explanation
7. Use Learn from Saksham
8. Listen to generated audio

All functionality works fully offline on Jetson using Llama 3.2:1B.
