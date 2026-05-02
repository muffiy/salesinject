from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Any
import datetime

from ...deps import get_db, get_current_user
from ....models import User, ScoutReport, PaperclipItem
from ....tasks import run_scout_mission, generate_ad_idea
from ....core.redis import get_redis
import redis

router = APIRouter()

# Helper function to transform map data
def transform_map_point(point):
    # Convert from {'lat': x, 'lng': y} to {'lon': y, 'lat': x, 'type': 'influencer'}
    return {
        'lon': point.get('lng', 0),
        'lat': point.get('lat', 0),
        'type': 'influencer'
    }

class ScoutMissionRequest(BaseModel):
    niche: str
    location: str = "Tunis"


class ScoutReportOut(BaseModel):
    id: str
    target_niche: Optional[str]
    target_location: Optional[str]
    map_data: List[dict]
    influencer_count: int
    created_at: datetime.datetime

    model_config = {"from_attributes": True}

class PaperclipItemOut(BaseModel):
    id: str
    item_type: str
    content: Any
    created_at: datetime.datetime

    model_config = {"from_attributes": True}

class ContentRequest(BaseModel):
    prompt: str


@router.post("/mission")
def launch_scout_mission(
    payload: ScoutMissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    r: redis.Redis = Depends(get_redis),
):
    """Launch an async scout mission via Celery."""
    # Prevent duplicate missions using a Redis lock
    lock_key = f"scout_lock:{current_user.id}"
    
    # Try to set the lock with a 5-minute timeout (300 seconds)
    if not r.set(lock_key, "running", ex=300, nx=True):
        raise HTTPException(
            status_code=409, 
            detail="A scout mission is already in progress. Please wait for it to complete."
        )

    task = run_scout_mission.delay(
        niche=payload.niche,
        location=payload.location,
        user_id=str(current_user.id),
        chat_id=current_user.telegram_id,
    )
    return {
        "status": "accepted",
        "task_id": task.id,
        "message": f"Scout mission for '{payload.niche}' in {payload.location} launched.",
    }


@router.get("/latest", response_model=ScoutReportOut)
def get_latest_scout_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the most recent scout report for the user."""
    report = (
        db.query(ScoutReport)
        .filter(ScoutReport.user_id == current_user.id)
        .order_by(ScoutReport.created_at.desc())
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="No scout reports found.")

    # Transform map data
    transformed_map_data = [transform_map_point(p) for p in (report.map_data or [])]

    return ScoutReportOut(
        id=str(report.id),
        target_niche=report.target_niche or "",
        target_location=report.target_location or "",
        map_data=transformed_map_data,
        influencer_count=report.influencer_count or 0,
        created_at=report.created_at,
    )


@router.get("/reports", response_model=List[ScoutReportOut])
def get_all_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all scout reports for the user."""
    reports = (
        db.query(ScoutReport)
        .filter(ScoutReport.user_id == current_user.id)
        .order_by(ScoutReport.created_at.desc())
        .limit(20)
        .all()
    )

    return [
        ScoutReportOut(
            id=str(r.id),
            target_niche=r.target_niche or "",
            target_location=r.target_location or "",
            map_data=[transform_map_point(p) for p in (r.map_data or [])],
            influencer_count=r.influencer_count or 0,
            created_at=r.created_at,
        )
        for r in reports
    ]


@router.get("/paperclips", response_model=List[PaperclipItemOut])
def get_user_paperclips(
    item_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return paperclip items (mission_log, pinned_profile, ad_copy, content_idea)."""
    query = db.query(PaperclipItem).filter(PaperclipItem.user_id == current_user.id)
    if item_type:
        query = query.filter(PaperclipItem.item_type == item_type)

    items = query.order_by(PaperclipItem.created_at.desc()).limit(50).all()

    return [
        PaperclipItemOut(
            id=str(item.id),
            item_type=item.item_type,
            content=item.content,
            created_at=item.created_at,
        )
        for item in items
    ]


@router.post("/generate")
def generate_content(
    payload: ContentRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate AI content idea via OpenRouter (async via Celery)."""
    task = generate_ad_idea.delay(
        user_id=str(current_user.id),
        prompt=payload.prompt,
    )
    return {
        "status": "accepted",
        "task_id": task.id,
        "message": "Content generation started.",
    }