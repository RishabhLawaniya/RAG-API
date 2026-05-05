from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from app.core.database import get_db
from app.services.embedding_service import create_single_embedding
from app.services.llm_service import generate_answer

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    document_ids: list[str]
    max_results: int = 5


class SourceChunk(BaseModel):
    chunk_id: str
    content: str
    page_number: int
    similarity: float


class QueryResponse(BaseModel):
    question: str
    answer: str                  # ← LLM generated answer
    sources: list[SourceChunk]   # ← chunks used to generate answer
    model: str
    tokens_used: int


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Full RAG pipeline:
    1. Embed question
    2. Vector search → find relevant chunks
    3. Send chunks + question to LLM
    4. Return answer with sources
    """

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if not request.document_ids:
        raise HTTPException(status_code=400, detail="At least one document_id required")

    # Step 1 — Embed the question
    print(f"\n🔍 Query: {request.question}")
    question_vector = create_single_embedding(request.question)

    # Step 2 — Vector similarity search
    sql = text("""
        SELECT
            c.id,
            c.content,
            c.page_number,
            1 - (c.embedding <=> CAST(:query_vector AS vector)) AS similarity
        FROM chunks c
        WHERE c.document_id = ANY(CAST(:doc_ids AS text[]))
          AND c.embedding IS NOT NULL
        ORDER BY c.embedding <=> CAST(:query_vector AS vector)
        LIMIT :limit
    """)

    vector_str = "[" + ",".join(str(x) for x in question_vector) + "]"

    result = db.execute(sql, {
        "query_vector": vector_str,
        "doc_ids": request.document_ids,
        "limit": request.max_results
    })

    rows = result.fetchall()

    if not rows:
        return QueryResponse(
            question=request.question,
            answer="No relevant content found in the provided documents.",
            sources=[],
            model="none",
            tokens_used=0
        )

    # Step 3 — Prepare chunks for LLM
    sources = [
        SourceChunk(
            chunk_id=str(row[0]),
            content=row[1],
            page_number=row[2],
            similarity=round(float(row[3]), 4)
        )
        for row in rows
    ]

    # Only pass top 3 most relevant chunks to LLM
    # (keeps prompt short and focused)
    top_chunks = [
        {"content": s.content, "page_number": s.page_number}
        for s in sources[:3]
    ]

    # Step 4 — Generate answer with LLM
    llm_result = generate_answer(request.question, top_chunks)

    return QueryResponse(
        question=request.question,
        answer=llm_result["answer"],
        sources=sources,
        model=llm_result["model"],
        tokens_used=llm_result["tokens_used"]
    )


@router.get("/query/test")
async def test_vector_search(db: Session = Depends(get_db)):
    count = db.execute(
        text("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL")
    ).scalar()

    return {
        "chunks_with_embeddings": count,
        "status": "ready" if count > 0 else "no embeddings found"
    }