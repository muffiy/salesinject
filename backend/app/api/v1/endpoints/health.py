from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any

from ... import deps

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
def health_check(db: Session = Depends(deps.get_db)):
    """
    Check the core health of the backend infrastructure.
    It verifies Postgres connectivity. Redis reachability is typically pinged inside the worker.
    """
    health_status = {
        "status": "healthy",
        "database": "offline"
    }
    
    # 1. Check Postgres Database Connectivity
    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = "online"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["database"] = "offline"
        health_status["database_error"] = str(e)
        
    return health_status
