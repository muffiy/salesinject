from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ... import deps
from ....models import User, Agent, UserTask, Task, Payment

router = APIRouter()


class UserOut(BaseModel):
    id: str
    username: Optional[str]
    first_name: Optional[str]
    role: str
    wallet_balance: float
    rank: str
    total_earnings: float
    tasks_completed: int
    active_agents: int

    model_config = {"from_attributes": True}


class PaymentOut(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    created_at: str

    model_config = {"from_attributes": True}


@router.get("/me", response_model=UserOut)
def get_me(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Return the authenticated user's profile with live stats."""
    tasks_done = (
        db.query(UserTask)
        .filter(UserTask.user_id == current_user.id, UserTask.status == "approved")
        .count()
    )
    active_agents = (
        db.query(Agent)
        .filter(Agent.user_id == current_user.id)
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
        tasks_completed=tasks_done,
        active_agents=active_agents,
    )


@router.get("/me/payments")
def get_payments(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Return the user's payment history (most recent first)."""
    payments = (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": str(p.id),
            "amount": float(p.amount),
            "currency": p.currency,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in payments
    ]
