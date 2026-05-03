"""
Earnings API — summary of user earnings and payout history.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...deps import get_db, get_current_user
from ....models import User, UserTask, PayoutTransaction

router = APIRouter()


@router.get("/")
def get_earnings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the user's earnings summary."""
    approved_tasks = (
        db.query(UserTask)
        .filter(UserTask.user_id == current_user.id, UserTask.status == "approved")
        .all()
    )
    task_earnings = sum(float(t.earnings or 0) for t in approved_tasks)

    recent_payouts = (
        db.query(PayoutTransaction)
        .filter(PayoutTransaction.user_id == current_user.id)
        .order_by(PayoutTransaction.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "total_earnings": float(current_user.total_earnings or 0),
        "wallet_balance": float(current_user.wallet_balance or 0),
        "task_earnings": task_earnings,
        "tasks_approved": len(approved_tasks),
        "recent_payouts": [
            {
                "id": str(p.id),
                "amount": float(p.amount),
                "currency": p.currency,
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in recent_payouts
        ],
    }
