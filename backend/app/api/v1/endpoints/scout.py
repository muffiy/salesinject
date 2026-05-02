from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Any
import datetime
import uuid

from ... import deps
from ....models import User, ScoutReport, PaperclipItem
from ....agent_os.war_engine import WarEngine

router = APIRouter()

class ScoutReportOut(BaseModel):
    id: str
    target_niche: Optional[str]
    map_data: List[Any]
    created_at: datetime.datetime

    model_config = {"from_attributes": True}

@router.get("/latest", response_model=ScoutReportOut)
def get_latest_scout_report(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Return the most recent scout report for the user."""
    report = db.query(ScoutReport).filter(
        ScoutReport.user_id == current_user.id
    ).order_by(ScoutReport.created_at.desc()).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="No scout reports found.")
        
    return ScoutReportOut(
        id=str(report.id),
        target_niche=report.target_niche or "",
        # Handle cases where map_data might be null in DB
        map_data=report.map_data if report.map_data is not None else [],
        created_at=report.created_at
    )


class PaperclipItemOut(BaseModel):
    id: str
    task_id: Optional[str]
    item_type: str
    content: Any
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


@router.get("/paperclips", response_model=List[PaperclipItemOut])
def get_user_paperclips(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Return all paperclip items (mission logs, pinned profiles, ad copies) globally for the user, ordered by newest first."""
    items = db.query(PaperclipItem).filter(
        PaperclipItem.user_id == current_user.id
    ).order_by(PaperclipItem.created_at.desc()).all()
    
    return [
        PaperclipItemOut(
            id=str(item.id),
            task_id=str(item.task_id) if item.task_id else None,
            item_type=item.item_type,
            content=item.content,
            created_at=item.created_at
        )
        for item in items
    ]


# Agent OS v2 Endpoints
class AgentOSMissionRequest(BaseModel):
    mission_type: str
    payload: dict
    fallback_mission: Optional[str] = None


class AgentOSMissionResponse(BaseModel):
    status: str
    trace_id: str
    session_id: str
    mission_type: str
    workflow: List[str]
    estimated_cost: float = 0.05


@router.post("/mission/v2", response_model=AgentOSMissionResponse)
async def launch_os_mission(
    request: AgentOSMissionRequest,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Launch an Agent OS v2 mission.

    Available mission types:
    - scout: Find and rank influencers
    - ammo_generation: Generate marketing content
    - bounty_match: Match brands with influencers
    - rapid_scout: Quick scout with minimal analysis
    - content_audit: Audit existing content
    - market_analysis: Analyze market trends
    """
    try:
        engine = WarEngine()

        # Launch mission
        result = await engine.launch_mission_with_fallback(
            mission_type=request.mission_type,
            user_id=str(current_user.id),
            payload=request.payload,
            fallback_mission=request.fallback_mission
        )

        return AgentOSMissionResponse(
            status=result["status"],
            trace_id=result["trace_id"],
            session_id=result["session_id"],
            mission_type=request.mission_type,
            workflow=result["workflow"],
            estimated_cost=0.05  # Default estimate
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Mission launch failed: {str(e)}"
        )


class MissionStatusResponse(BaseModel):
    trace_id: str
    status: str
    mission_type: str
    user_id: str
    started_at: Optional[float]
    progress: dict
    last_error: Optional[str]
    result: Optional[dict]


@router.get("/mission/v2/{trace_id}/status", response_model=MissionStatusResponse)
async def get_mission_status(
    trace_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    """Get status of an Agent OS v2 mission."""
    engine = WarEngine()
    status = engine.get_mission_status(trace_id)

    # Verify user owns this mission
    if status.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this mission"
        )

    return MissionStatusResponse(**status)


@router.get("/mission/v2/user/missions")
async def list_user_missions(
    mission_type: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(deps.get_current_user)
):
    """List Agent OS v2 missions for the current user."""
    engine = WarEngine()
    missions = engine.list_user_missions(
        user_id=str(current_user.id),
        limit=limit,
        mission_type=mission_type
    )

    return {
        "user_id": str(current_user.id),
        "count": len(missions),
        "missions": missions
    }


@router.post("/mission/v2/{trace_id}/cancel")
async def cancel_mission(
    trace_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    """Cancel a running Agent OS v2 mission."""
    engine = WarEngine()
    cancelled = engine.cancel_mission(trace_id, str(current_user.id))

    if not cancelled:
        raise HTTPException(
            status_code=404,
            detail="Mission not found, not running, or not owned by user"
        )

    return {"status": "cancelled", "trace_id": trace_id}
