import asyncio
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

def build_engine():
    return create_engine(
        settings.SYNC_DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True
    )
    return create_engine(url, pool_size=5, max_overflow=10, pool_pre_ping=True)

engine = build_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    loop = asyncio.get_event_loop()
    db = await loop.run_in_executor(None, SessionLocal)
    try:
        yield db
        await loop.run_in_executor(None, db.commit)
    except Exception:
        await loop.run_in_executor(None, db.rollback)
        raise
    finally:
        await loop.run_in_executor(None, db.close)
