from fastapi import APIRouter, Depends
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
