"""
Async Database Layer with pgvector support.

Supports: Content Generation, Multi-Session, Vector Search.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config_v2 import settings

logger = logging.getLogger(__name__)

# ── Async Engine ─────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    future=True,
)

# ── Session Factory ──────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# ── Base Model ───────────────────────────────────────────────────────────────
Base = declarative_base()


# ── pgvector Extension Setup ─────────────────────────────────────────────────
async def init_pgvector() -> None:
    """Initialize pgvector and pg_trgm extensions on startup."""

    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    logger.info("✅ pgvector and pg_trgm extensions initialized")


# ── Database Dependency ──────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    """FastAPI dependency for database sessions."""

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncSession:
    """Context manager for database sessions (e.g., background workers)."""

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Connection Health Check ──────────────────────────────────────────────────
async def check_db_health() -> dict:
    """Check database connectivity and basic performance info."""

    import time

    start = time.time()
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT version(), pg_size_pretty(pg_database_size(current_database()))"),
            )
            row = result.fetchone()
            latency = (time.time() - start) * 1000
            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "version": row[0] if row else None,
                "size": row[1] if row else None,
            }
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}

