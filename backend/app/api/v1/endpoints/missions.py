from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ...deps import get_db, get_current_user
from ....models import User, UserTask, Task, PayoutTransaction

router = APIRouter()


@router.get('/history')
def get_mission_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the user's completed mission history."""
    submissions = (
        db.query(UserTask)
        .filter(UserTask.user_id == current_user.id)
        .order_by(UserTask.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": str(s.id),
            "task_id": str(s.task_id),
            "status": s.status,
            "earnings": float(s.earnings or 0),
            "submission_url": s.submission_url,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "approved_at": s.approved_at.isoformat() if s.approved_at else None,
        }
        for s in submissions
    ]


@router.post('/{claim_id}/boost')
def boost_mission(claim_id: str, reward: float = 15.0):
    return {'claimId': claim_id, 'newReward': round(reward * 1.3, 2), 'reviewMode': 'strict'}


@router.post('/share/{mission_id}')
def share_mission(mission_id: str):
    return {'missionId': mission_id, 'bonus': 2, 'granted': True}


@router.post('/re-run/{trace_id}')
def rerun_mission(trace_id: str):
    return {'trace_id': trace_id, 'boosted_reward_multiplier': 1.2, 'redirect': f'/mission/{trace_id}'}
