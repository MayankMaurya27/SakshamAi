# Backend Technical Specification v1.0

## Saksham AI

---

# 1. Backend Goal

Build a fully offline FastAPI backend that powers:

* Learn from Document
* Learn from Saksham
* RAG Question Answering
* Quiz Generation
* Hindi Explanation
* Summarization
* Audio Learning

The backend must run entirely on local hardware and be compatible with NVIDIA Jetson Orin Nano.

---

# 2. Backend Folder Structure

backend/

├── app.py

├── config/
│   ├── settings.py
│   └── constants.py

├── api/
│   ├── upload.py
│   ├── ask.py
│   ├── summary.py
│   ├── quiz.py
│   ├── hindi.py
│   └── documents.py

├── services/
│   ├── rag_service.py
│   ├── summary_service.py
│   ├── quiz_service.py
│   ├── accessibility_service.py
│   ├── audio_service.py
│   └── knowledge_service.py

├── ai/
│   ├── embeddings.py
│   ├── llm.py
│   ├── retriever.py
│   ├── prompt_builder.py
│   └── faiss_manager.py

├── documents/
│   ├── pdf_parser.py
│   ├── chunker.py
│   ├── processor.py
│   └── indexer.py

├── database/
│   ├── models.py
│   ├── db.py
│   └── repositories.py

├── data/
│   ├── uploads/
│   ├── faiss/
│   ├── audio/
│   └── saksham_kb/

├── tests/

└── requirements.txt

---

# 3. Core Services

## 3.1 LLM Service

File:

ai/llm.py

Responsibilities:

* Connect to Ollama
* Send prompts
* Receive responses
* Handle failures

Functions:

generate_answer()

generate_summary()

generate_quiz()

generate_hindi_response()

---

## 3.2 Embedding Service

File:

ai/embeddings.py

Model:

multilingual-e5-small

Responsibilities:

* Generate embeddings
* Batch embedding support

Functions:

embed_text()

embed_batch()

---

## 3.3 FAISS Manager

File:

ai/faiss_manager.py

Responsibilities:

* Create index
* Save index
* Load index
* Search vectors

Functions:

create_index()

save_index()

load_index()

search()

---

## 3.4 Retriever Service

File:

ai/retriever.py

Responsibilities:

* Query FAISS
* Retrieve metadata
* Return top chunks

Functions:

retrieve_document_context()

retrieve_saksham_context()

---

# 4. Document Processing Layer

## PDF Parser

File:

documents/pdf_parser.py

Library:

PyMuPDF

Responsibilities:

* Extract text
* Extract page metadata

Function:

extract_text()

---

## Chunking Service

File:

documents/chunker.py

Chunk Size:

700 tokens

Chunk Overlap:

100 tokens

Function:

create_chunks()

---

## Indexer

File:

documents/indexer.py

Responsibilities:

* Generate embeddings
* Insert into FAISS
* Save metadata

Function:

index_document()

---

# 5. Database Design

Database:

SQLite

File:

saksham.db

---

Table: documents

Columns:

id
filename
filepath
uploaded_at
summary
key_concepts

---

Table: chunks

Columns:

id
document_id
chunk_index
chunk_text

---

Table: quizzes

Columns:

id
document_id
question
option_a
option_b
option_c
option_d
correct_answer

---

# 6. Learning Modes

Mode:

LEARN

Prompt:

Explain clearly using educational language.

---

Mode:

SIMPLIFY

Prompt:

Explain as if teaching a Class 6 student.

Use simple words.

Use examples.

---

Mode:

HINDI

Prompt:

Explain entirely in Hindi.

Maintain educational terminology.

---

Mode:

QUIZ

Prompt:

Generate 5 MCQs.

Provide answers.

---

Mode:

SUMMARY

Prompt:

Generate concise revision notes.

---

# 7. Learn from Document Flow

PDF Upload
↓
Text Extraction
↓
Chunking
↓
Embedding Generation
↓
FAISS Indexing
↓
SQLite Metadata
↓
Auto Analysis
├─ Summary
├─ Key Concepts
└─ Quiz
↓
Ready for Queries

---

# 8. Learn from Saksham Flow

User Selects:

Class
↓
Subject
↓
Topic

↓

Knowledge Service

↓

Retrieve Context

↓

Llama 3.2

↓

Learning Output

---

# 9. Educational Knowledge Base

Structure:

saksham_kb/

class6/
class7/
class8/
class9/
class10/

Each topic stored as:

JSON

Example:

{
"class": 8,
"subject": "Science",
"topic": "Force",
"content": "..."
}

---

# 10. API Contracts

POST /upload

Input:

multipart/form-data

Output:

{
"document_id": 1,
"summary": "...",
"key_concepts": [...]
}

---

POST /ask

Input:

{
"question":"...",
"source":"document"
}

Output:

{
"answer":"..."
}

---

POST /simplify

Input:

{
"question":"..."
}

Output:

{
"simplified_answer":"..."
}

---

POST /quiz

Input:

{
"document_id":1
}

Output:

{
"questions":[]
}

---

POST /hindi

Input:

{
"question":"..."
}

Output:

{
"answer":"..."
}

---

# 11. Error Handling

Handle:

* Empty PDF
* Corrupted PDF
* Missing FAISS index
* Missing embeddings
* Ollama unavailable
* Invalid document id

All errors must return structured JSON.

---

# 12. Testing Strategy

Unit Tests

* Embeddings
* Retrieval
* Chunking
* PDF Extraction

Integration Tests

* Upload → Query
* Upload → Summary
* Upload → Quiz

End-to-End Tests

* Learn from Document
* Learn from Saksham
* Hindi Mode
* Simplify Mode
* Audio Mode

---

# 13. Performance Targets

PDF Processing:

< 20 seconds

Question Answering:

< 8 seconds

Summary Generation:

< 15 seconds

Quiz Generation:

< 15 seconds

---

# 14. MVP Completion Criteria

Backend is complete when:

✓ PDF Upload Works

✓ Document Stored

✓ FAISS Retrieval Works

✓ Learn from Saksham Works

✓ Summary Generation Works

✓ Quiz Generation Works

✓ Hindi Mode Works

✓ Simplify Mode Works

✓ Audio Generation Works

✓ Fully Offline Execution Works
