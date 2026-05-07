import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException

# Where uploaded files will be stored
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True) 
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB in bytes
ALLOWED_TYPES = ["application/pdf"]

async def save_upload_file(file: UploadFile) -> dict:
    """
    Validates and saves an uploaded file to disk.
    Returns file metadata (id, path, filename).
    """

    # --- Validation ---

    # 1. Check file type by content-type header
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are allowed. You sent: {file.content_type}"
        )

    # 2. Read file bytes into memory
    file_bytes = await file.read()

    # 3. Check file size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is 10MB, you sent {len(file_bytes) / 1024 / 1024:.1f}MB"
        )

    # 4. Check file isn't empty
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    # --- Save to disk ---

    # Generate a unique ID for this document
    document_id = str(uuid.uuid4())  # e.g. "a3f2c1d4-..."

    # Create a safe filename using the unique ID (ignore original filename for security)
    safe_filename = f"{document_id}.pdf"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Write bytes to disk asynchronously
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_bytes)

    return {
        "document_id": document_id,
        "file_path": file_path,
        "original_filename": file.filename,
        "file_size": len(file_bytes)
    }