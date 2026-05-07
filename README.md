# RAG Document Q&A API

A production-grade Retrieval-Augmented Generation (RAG) API that allows users to upload PDF documents and ask questions about them using semantic search and LLM.

## Tech Stack

| Component | Technology |
|---|---|
| API Framework | FastAPI |
| Database | PostgreSQL + pgvector (Supabase) |
| ORM + Migrations | SQLAlchemy + Alembic |
| Task Queue | Celery + Redis |
| PDF Parsing | PyMuPDF |
| Text Chunking | LangChain text splitters |
| Embeddings | sentence-transformers (local) |
| Vector Search | pgvector cosine similarity |
| LLM | Llama 3 via Groq |
| Deployment | Docker + docker-compose |

## Architecture

PDF Upload → Celery Worker → PDF Parsing → Chunking → Embeddings → pgvector
↓
User Query → Embed Question → Cosine Similarity Search → Top Chunks → LLM → Answer

## Features

- Async PDF upload and processing via Celery
- Semantic search using vector embeddings
- Natural language answers with source attribution
- Task status tracking
- Auto-generated Swagger docs at `/docs`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/documents` | Upload PDF document |
| GET | `/api/v1/documents/{id}/status` | Check processing status |
| GET | `/api/v1/documents` | List all documents |
| POST | `/api/v1/query` | Ask a question |
| GET | `/api/v1/tasks/{task_id}` | Check Celery task status |
| GET | `/api/v1/health` | Health check |

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL with pgvector extension
- Redis

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/rag-api.git
cd rag-api

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:

```env
DATABASE_URL=your_database_url
SYNC_DATABASE_URL=your_sync_database_url
REDIS_URL=redis://localhost:6379/0
GROQ_API_KEY=your_groq_key
```

### Run with Docker

```bash
docker-compose up --build
```

### Run manually

```bash
# Terminal 1 - API
uvicorn app.main:app --reload

# Terminal 2 - Celery worker
celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

## Example Usage

### Upload a document
```bash
curl -X POST http://localhost:8000/api/v1/documents -F "file=@document.pdf"

for eg.

curl -X POST http://localhost:8000/api/v1/documents -F "file=@C:\Users\Rishabh\Downloads\xyz.pdf"
```

### Ask a question
```bash
curl -X POST http://localhost:8000/api/v1/query ^
  -H "Content-Type: application/json" ^
  -d '{"question": "What is the educational background?", "document_ids": ["your-doc-id"]}'

for eg.

curl -X POST http://localhost:8000/api/v1/query ^
-H "Content-Type: application/json" ^
-d "{\"question\": \"What is the educational background?\", \"document_ids\": [\"f72dc7bd-26da-4d95-88a4-1ecff96f898b\"]}"
