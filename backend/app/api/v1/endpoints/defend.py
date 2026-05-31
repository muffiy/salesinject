"""
Defend Endpoints for Agent OS v2.
Contains defensive skills like visibility shield.
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from app.core.redis_client import r
from app.api.deps import get_current_user

router = APIRouter(prefix="/defend", tags=["Defend"])


@router.post("/shield")
async def visibility_shield(hours: int, user = Depends(get_current_user)):
    """
    Activate visibility shield to prevent rank decay for specified duration.

    Args:
        hours: Number of hours to activate the shield

    Returns:
        Shield activation details
    """
    if hours <= 0 or hours > 720:  # Max 30 days
        raise HTTPException(status_code=400, detail="Hours must be between 1 and 720")

    key = f"shield:{user.id}"
    r.setex(key, hours * 3600, "active")

    expiry_time = datetime.utcnow() + timedelta(hours=hours)

    return {
        "shield_active": True,
        "shield_active_until": expiry_time.isoformat(),
        "hours": hours
    }