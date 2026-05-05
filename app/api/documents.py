from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db, SessionLocal
from app.models.document import Document
from app.services.file_service import save_upload_file
from app.tasks.document_tasks import process_document_task

router = APIRouter()

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str
    task_id: str    # ← new: Celery task ID for tracking


@router.post("/documents", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Save file to disk
    file_meta = await save_upload_file(file)

    # 2. Create document record in DB
    document = Document(
        id=file_meta["document_id"],
        filename=file_meta["original_filename"],
        file_path=file_meta["file_path"],
        status="pending"
    )
    db.add(document)
    db.commit()

    # 3. Send task to Celery (non-blocking — returns immediately)
    #    .delay() is shorthand for .apply_async()
    task = process_document_task.delay(
        file_meta["document_id"],
        file_meta["file_path"]
    )

    print(f"📤 Task dispatched: {task.id}")

    return UploadResponse(
        document_id=file_meta["document_id"],
        filename=file_meta["original_filename"],
        status="pending",
        message="Document uploaded. Celery worker is processing it.",
        task_id=task.id     # return task ID so client can track it
    )


@router.get("/documents/{document_id}/status")
async def get_document_status(
    document_id: str,
    db: Session = Depends(get_db)
):
    db.expire_all()  # ← this line forces fresh read from DB

    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document_id": document.id,
        "filename": document.filename,
        "status": document.status,
        "chunk_count": document.chunk_count,
        "error": document.error_message,
        "created_at": document.created_at
    }


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Check Celery task status directly.
    This is separate from document status — shows raw Celery state.
    """
    from app.core.celery_app import celery_app
    from celery.result import AsyncResult

    task = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "celery_status": task.status,   # PENDING/STARTED/SUCCESS/FAILURE
        "result": task.result if task.successful() else None,
        "error": str(task.result) if task.failed() else None
    }