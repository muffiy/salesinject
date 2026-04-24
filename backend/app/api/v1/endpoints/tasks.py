from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid

from ... import deps
from ....models import User, Task, UserTask

router = APIRouter()


class TaskOut(BaseModel):
    id: str
    title: Optional[str]
    description: Optional[str]
    niche: Optional[str]
    reward_amount: float
    status: str
    deadline: Optional[str]

    model_config = {"from_attributes": True}


class UserTaskOut(BaseModel):
    id: str
    task_id: str
    task_title: Optional[str]
    status: str
    earnings: float
    submission_url: Optional[str]
    created_at: Optional[str]

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[TaskOut])
def list_tasks(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Return all open tasks available to claim."""
    tasks = db.query(Task).filter(Task.status == "open").order_by(Task.created_at.desc()).all()
    return [
        TaskOut(
            id=str(t.id),
            title=t.title or "",
            description=t.description or "",
            niche=t.niche or "",
            reward_amount=float(t.reward_amount or 0),
            status=t.status or "open",
            deadline=t.deadline.isoformat() if t.deadline else None,
        )
        for t in tasks
    ]


@router.post("/{task_id}/claim", status_code=201)
def claim_task(
    task_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Claim an open task — creates a pending UserTask submission."""
    try:
        tid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task_id.")

    task = db.query(Task).filter(Task.id == tid, Task.status == "open").first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or not open.")

    # Prevent double-claiming
    existing = db.query(UserTask).filter(
        UserTask.user_id == current_user.id,
        UserTask.task_id == tid,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You already claimed this task.")

    user_task = UserTask(
        user_id=current_user.id,
        task_id=tid,
        status="pending",
        submission_url="",
        earnings=task.reward_amount,
    )
    db.add(user_task)
    db.commit()
    db.refresh(user_task)
    return {"id": str(user_task.id), "status": "pending", "task_id": task_id}


@router.get("/me/submissions")
def my_submissions(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Return the user's active task submissions with their task details."""
    user_tasks = (
        db.query(UserTask)
        .filter(UserTask.user_id == current_user.id)
        .order_by(UserTask.created_at.desc())
        .limit(20)
        .all()
    )
    results = []
    for ut in user_tasks:
        task = db.query(Task).filter(Task.id == ut.task_id).first()
        results.append({
            "id": str(ut.id),
            "task_id": str(ut.task_id),
            "task_title": task.title if task else "",
            "task_niche": task.niche if task else "",
            "reward_amount": float(task.reward_amount or 0) if task else 0,
            "status": ut.status,
            "earnings": float(ut.earnings or 0),
            "submission_url": ut.submission_url or "",
            "created_at": ut.created_at.isoformat() if ut.created_at else None,
        })
    return results


@router.post("/{task_id}/approve")
def approve_submission(
    task_id: str,
    submission_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Approve a UserTask submission (brand only).
    Triggers agent_learning_task to embed the content into agent memories.
    """
    from ....tasks import agent_learning_task
    from datetime import datetime, timezone

    ut = db.query(UserTask).filter(UserTask.id == submission_id).first()
    if not ut:
        raise HTTPException(status_code=404, detail="Submission not found.")

    task = db.query(Task).filter(Task.id == ut.task_id).first()
    if not task or str(task.brand_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Only the brand can approve this task.")

    ut.status = "approved"
    ut.approved_at = datetime.now(timezone.utc)
    db.commit()

    # Kick off learning async — if agent was used
    if ut.agent_id and ut.submission_url:
        agent_learning_task.delay(
            str(ut.agent_id),
            str(ut.id),
            ut.submission_url,
        )

    return {"status": "approved"}
