from app.core.celery_app import celery_app
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services.pdf_service import process_pdf
from app.services.embedding_service import create_embeddings


def get_worker_db():
    url = URL.create(
        drivername="postgresql+psycopg2",
        username="postgres",
        password="Rishabh@2401",
        host="db.zaagdlnecpymghccgscj.supabase.co",
        port=5432,
        database="postgres"
    )
    engine = create_engine(url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


@celery_app.task(
    bind=True,
    name="process_document",
    max_retries=3,
    default_retry_delay=60
)
def process_document_task(self, document_id: str, file_path: str):
    from app.models.document import Document, Chunk

    db = get_worker_db()

    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return

        document.status = "processing"
        db.commit()
        print(f"⚙️  Processing: {document.filename}")

        chunks_data = process_pdf(file_path)
        print(f"✂️  Created {len(chunks_data)} chunks")

        texts = [chunk["content"] for chunk in chunks_data]
        vectors = create_embeddings(texts)

        chunks = [
            Chunk(
                document_id=document_id,
                content=chunk["content"],
                page_number=chunk["page_number"],
                chunk_index=chunk["chunk_index"],
                embedding=vectors[i]
            )
            for i, chunk in enumerate(chunks_data)
        ]
        db.add_all(chunks)

        document.status = "ready"
        document.chunk_count = len(chunks)
        db.commit()

        print(f"✅ Document ready — {len(chunks)} chunks with embeddings saved")
        return {"document_id": document_id, "chunk_count": len(chunks)}

    except Exception as exc:
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document and self.request.retries >= self.max_retries:
                document.status = "failed"
                document.error_message = str(exc)
                db.commit()
        except Exception:
            pass

        print(f"❌ Failed (attempt {self.request.retries + 1}): {exc}")
        raise self.retry(exc=exc)

    finally:
        db.close()