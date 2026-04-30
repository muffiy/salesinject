"""
Agents API — CRUD for user-owned AI agents (Scout, Matchmaker, Content Gen).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, constr
from typing import Optional, List
import uuid

from ...deps import get_db, get_current_user
from ....models import User, Agent

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class AgentCreate(BaseModel):
    name: constr(min_length=1, max_length=100, strip_whitespace=True)
    niche: constr(min_length=1, max_length=100, strip_whitespace=True)
    agent_type: str = "scout"  # scout, matchmaker, content_gen


class AgentOut(BaseModel):
    id: str
    name: str
    niche: str
    agent_type: str
    performance_score: float
    tasks_completed: int
    total_earnings: float
    is_active: bool

    model_config = {"from_attributes": True}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[AgentOut])
def list_agents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all agents owned by the current user."""
    agents = db.query(Agent).filter(Agent.user_id == current_user.id).all()
    return [_agent_to_out(a) for a in agents]


@router.post("/", response_model=AgentOut, status_code=201)
def create_agent(
    payload: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new AI agent for the current user."""
    agent = Agent(
        user_id=current_user.id,
        name=payload.name,
        niche=payload.niche,
        agent_type=payload.agent_type,
        configuration={},
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return _agent_to_out(agent)


@router.delete("/{agent_id}", status_code=204)
def delete_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _agent_to_out(agent: Agent) -> AgentOut:
    return AgentOut(
        id=str(agent.id),
        name=agent.name or "",
        niche=agent.niche or "",
        agent_type=agent.agent_type or "scout",
        performance_score=float(agent.performance_score or 0),
        tasks_completed=int(agent.tasks_completed or 0),
        total_earnings=float(agent.total_earnings or 0),
        is_active=agent.is_active if agent.is_active is not None else True,
    )
