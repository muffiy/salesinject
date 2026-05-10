from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any

from ...deps import get_db

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
def health_check(db: Session = Depends(get_db)):
    """Check backend infrastructure health — Postgres connectivity."""
    health_status = {
        "status": "healthy",
        "database": "offline",
        "version": "1.0.0",
    }

    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = "online"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["database_error"] = str(e)

    return health_status


@router.get("/ready")
async def health_ready():
    """Deep health check — validates DB, Redis, and Celery connectivity."""
    checks: Dict[str, str] = {}

    # Database check
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    # Redis check
    try:
        from app.core.redis_client import r as redis_client
        redis_client.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"

    # Celery worker check
    try:
        from app.worker import celery_app
        with celery_app.connection() as conn:
            conn.ensure_connection(max_retries=1)
        checks["celery"] = "ok"
    except ImportError:
        checks["celery"] = "not_installed"
    except Exception as e:
        checks["celery"] = f"error: {e}"

    all_ok = all(v == "ok" for v in checks.values())
    return JSONResponse(
        content={
            "status": "ok" if all_ok else "degraded",
            "checks": checks,
        },
        status_code=200 if all_ok else 503,
    )
