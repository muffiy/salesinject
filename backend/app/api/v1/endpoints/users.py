"""
Users API — profile, stats, payments, leaderboard.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from ...deps import get_db, get_current_user
from ....models import User, Agent, UserTask, PayoutTransaction, Leaderboard

router = APIRouter()


class UserOut(BaseModel):
    id: str
    username: Optional[str]
    first_name: Optional[str]
    role: str
    wallet_balance: float
    rank: str
    total_earnings: float
    streak_days: int
    tasks_completed: int
    active_agents: int

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    username: Optional[str]
    rank_position: int
    score: float
    offers_completed: int


@router.get("/me", response_model=UserOut)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the authenticated user's profile with live stats."""
    tasks_done = (
        db.query(UserTask)
        .filter(UserTask.user_id == current_user.id, UserTask.status == "approved")
        .count()
    )
    active_agents = (
        db.query(Agent)
        .filter(Agent.user_id == current_user.id, Agent.is_active == True)
        .count()
    )
    return UserOut(
        id=str(current_user.id),
        username=current_user.username or "",
        first_name=current_user.first_name or "",
        role=current_user.role or "creator",
        wallet_balance=float(current_user.wallet_balance or 0),
        rank=current_user.rank or "bronze",
        total_earnings=float(current_user.total_earnings or 0),
        streak_days=current_user.streak_days or 0,
        tasks_completed=tasks_done,
        active_agents=active_agents,
    )


@router.get("/me/payments")
def get_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the user's payment/payout history (most recent first)."""
    payments = (
        db.query(PayoutTransaction)
        .filter(PayoutTransaction.user_id == current_user.id)
        .order_by(PayoutTransaction.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": str(p.id),
            "amount": float(p.amount),
            "currency": p.currency,
            "status": p.status,
            "payment_method": p.payment_method,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in payments
    ]


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    """Return the global leaderboard."""
    entries = (
        db.query(Leaderboard)
        .order_by(Leaderboard.rank_position.asc())
        .limit(limit)
        .all()
    )
    return [
        LeaderboardEntry(
            username=e.username,
            rank_position=e.rank_position,
            score=float(e.score or 0),
            offers_completed=e.offers_completed or 0,
        )
        for e in entries
    ]


@router.get("/progress")
def get_user_progress(current_user: User = Depends(get_current_user)):
    """Return the user's XP, level, and reputation progress."""
    return {
        "xp": current_user.xp or 0,
        "level": current_user.level or 1,
        "reputation_score": current_user.reputation_score or 0,
        "rank": current_user.rank or "bronze",
    }


@router.get("/me/profile")
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a rich user profile for the Agent OS profile page."""
    tasks_done = (
        db.query(UserTask)
        .filter(UserTask.user_id == current_user.id, UserTask.status == "approved")
        .count()
    )
    active_agents = (
        db.query(Agent)
        .filter(Agent.user_id == current_user.id, Agent.is_active == True)
        .count()
    )
    return {
        "id": str(current_user.id),
        "username": current_user.username or "",
        "first_name": current_user.first_name or "",
        "role": current_user.role or "creator",
        "wallet_balance": float(current_user.wallet_balance or 0),
        "rank": current_user.rank or "bronze",
        "total_earnings": float(current_user.total_earnings or 0),
        "streak_days": current_user.streak_days or 0,
        "tasks_completed": tasks_done,
        "active_agents": active_agents,
        "xp": current_user.xp or 0,
        "level": current_user.level or 1,
        "reputation_score": current_user.reputation_score or 0,
        "onboarded": current_user.onboarded or False,
    }
