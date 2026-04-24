from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, constr
from typing import Optional
import uuid

from ... import deps
from ....models import User, Agent

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class AgentCreate(BaseModel):
    name: constr(min_length=1, max_length=100, strip_whitespace=True)
    niche: constr(min_length=1, max_length=100, strip_whitespace=True)


class AgentOut(BaseModel):
    id: str
    name: Optional[str]
    niche: Optional[str]
    performance_score: float
    tasks_completed: int
    total_earnings: float

    model_config = {"from_attributes": True}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _agent_to_out(agent: Agent) -> AgentOut:
    return AgentOut(
        id=str(agent.id),
        name=agent.name or "",
        niche=agent.niche or "",
        performance_score=float(agent.performance_score or 0),
        tasks_completed=int(agent.tasks_completed or 0),
        total_earnings=float(agent.total_earnings or 0),
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[AgentOut])
def list_agents(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Return all agents owned by the current user."""
    agents = db.query(Agent).filter(Agent.user_id == current_user.id).all()
    return [_agent_to_out(a) for a in agents]


@router.post("/", response_model=AgentOut, status_code=201)
def create_agent(
    payload: AgentCreate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Create a new agent for the current user."""
    agent = Agent(
        user_id=current_user.id,
        name=payload.name,
        niche=payload.niche,
        configuration={},  # default empty config; extended in Phase 5
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return _agent_to_out(agent)


@router.delete("/{agent_id}", status_code=204)
def delete_agent(
    agent_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Delete an agent — only the owner may do this."""
    try:
        aid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent_id format.")

    agent = db.query(Agent).filter(Agent.id == aid).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found.")
    if agent.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this agent.")

    db.delete(agent)
    db.commit()
    return None
