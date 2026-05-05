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