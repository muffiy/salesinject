from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, constr
from celery.result import AsyncResult
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..api import deps
from ..models import User
from ..tasks import run_agent_task

router = APIRouter(prefix="/agent", tags=["Agent"])
limiter = Limiter(key_func=get_remote_address)


class AgentTaskRequest(BaseModel):
    niche: constr(min_length=1, max_length=100)       # validated / sanitised
    product_name: constr(min_length=1, max_length=200)
    agent_id: str | None = None
    action_type: str = "ad_gen"


@router.post("/task")
@limiter.limit("5/minute")
async def submit_agent_task(
    request: Request,
    payload: AgentTaskRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Enqueue an agent task via Celery.
    Returns 202 Accepted with a task_id for polling.
    Phase 5 will inject RAG context (memories, ad_examples) before dispatch.
    """
    if payload.action_type == "scout":
        if float(current_user.wallet_balance or 0) < 100:
            raise HTTPException(status_code=400, detail="Insufficient credits. 100 required for a Scout mission.")
        try:
            current_user.wallet_balance = float(current_user.wallet_balance or 0) - 100
            db.flush()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=503, detail="Service Unavailable: Database connection currently offline.")

    celery_payload = {
        "niche": payload.niche,
        "product_name": payload.product_name,
        "agent_id": payload.agent_id,
        "action_type": payload.action_type,
        # Phase 5 RAG: memories & ad_examples injected here
        "memories": [],
        "ad_examples": [],
    }

    try:
        task = run_agent_task.delay(str(current_user.id), celery_payload)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail="Service Unavailable: Task queue is offline. Your credits have been safely refunded.")

    return {
        "status": "accepted",
        "task_id": task.id,
        "message": "Agent task queued. Poll /agent/task/{task_id}/status for results.",
    }


@router.get("/task/{task_id}/status")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Poll Celery task state.
    Returns one of: PENDING | STARTED | RETRY | FAILURE | SUCCESS
    On SUCCESS, includes the full result (ad_idea dict).
    """
    result = AsyncResult(task_id)

    response: dict = {"task_id": task_id, "state": result.state}

    if result.state == "SUCCESS":
        response["result"] = result.result
    elif result.state == "FAILURE":
        response["error"] = str(result.result)

    return response
