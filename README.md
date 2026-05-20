# 📌 RAG Document Q&A API

A scalable backend system that enables users to upload PDF documents and query them using semantic search and LLM-powered responses.

🚀 Key Features:

-> Asynchronous document processing using Celery + Redis

-> PDF parsing, chunking, and embedding pipeline

-> Semantic search using pgvector (PostgreSQL)

-> Context-aware answers using LLM (Llama 3 via Groq)

-> REST APIs with FastAPI and auto Swagger docs (/docs)

# 🏗️ Architecture Overview

PDF Upload → FastAPI → Celery → Redis → Worker
                                ↓
                        PDF Parsing → Chunking → Embeddings → PostgreSQL (pgvector)

User Query → Embed Query → Vector Search → Top Chunks → LLM → Answer


# 🛠️ Tech Stack

1. Backend: FastAPI
2. Database: PostgreSQL + pgvector
3. Queue: Celery + Redis
4. ORM: SQLAlchemy + Alembic
5. Embeddings: sentence-transformers
6. LLM: Llama 3 (via Groq)

## ⚙️ Local Setup (Step-by-Step)

1. Clone repository
git clone https://github.com/YOUR_USERNAME/rag-api.git
cd rag-api
2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
OR
source venv/bin/activate  # Mac/Linux
3. Install dependencies
pip install -r requirements.txt
4. Setup environment variables

* Create a .env file:

* DATABASE_URL=

* SYNC_DATABASE_URL=

* REDIS_URL=redis://localhost:6379/0

* GROQ_API_KEY=

5. Start services
Option A: Using Docker (recommended)
docker-compose up --build

## Manual setup

### Terminal 1:

uvicorn app.main:app --reload

### Terminal 2:

celery -A app.core.celery_app worker --loglevel=info --pool=solo

## 📡 API Usage

Upload PDF
curl -X POST http://localhost:8000/api/v1/documents \
-F "file=@document.pdf"

Query document
curl -X POST http://localhost:8000/api/v1/query \
-H "Content-Type: application/json" \
-d '{"question": "Your question", "document_ids": ["<doc-id>"]}'

📊 Example Flow

1. Upload a PDF
2. Background worker processes it (chunking + embeddings)
3. Ask a question
4. System retrieves relevant chunks
5. LLM generates contextual answer
   
🧠 Key Learnings
Designing async pipelines using Celery
Managing background job retries and failures
Implementing vector search using pgvector
Integrating LLMs for contextual responses
🔗 API Docs

Swagger UI available at:

http://localhost:8000/docs
