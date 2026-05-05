from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import router as general_router
from app.api.documents import router as documents_router
from app.api.query import router as query_router      # ← add this

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(general_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(query_router, prefix="/api/v1")    # ← add this

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}