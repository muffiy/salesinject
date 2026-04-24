from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Any
import datetime

from ... import deps
from ....models import User, ScoutReport, PaperclipItem

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
