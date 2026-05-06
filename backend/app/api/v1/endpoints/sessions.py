from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ... import deps
from ....models import User
from ....services.session_service_v2 import session_service

router = APIRouter()


class CreateSessionRequest(BaseModel):
    agent_type: str = Field(min_length=1, max_length=100)
    parent_session_id: Optional[str] = None
    context: Optional[dict[str, Any]] = None


class SessionResponse(BaseModel):
    id: str
    user_id: str
    agent_type: Optional[str]
    parent_session_id: Optional[str]
    status: str
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


@router.post("/", response_model=SessionResponse)
async def create_session(
    req: CreateSessionRequest,
    current_user: User = Depends(deps.get_current_user),
):
    try:
        session = await session_service.create_session(
            user_id=str(current_user.id),
            agent_type=req.agent_type,
            parent_session_id=req.parent_session_id,
            context=req.context,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return SessionResponse(
        id=str(session.id),
        user_id=str(session.user_id),
        agent_type=session.agent_type,
        parent_session_id=str(session.parent_session_id) if session.parent_session_id else None,
        status=session.status or "active",
        created_at=session.created_at.isoformat() if session.created_at else None,
        completed_at=session.completed_at.isoformat() if session.completed_at else None,
    )


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    current_user: User = Depends(deps.get_current_user),
):
    session = await session_service.get_session(session_id=session_id)
    if not session or session.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/{session_id}/resume")
async def resume_session(
    session_id: str,
    current_user: User = Depends(deps.get_current_user),
):
    session = await session_service.resume_session(session_id=session_id, user_id=str(current_user.id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "resumed", "session_id": session_id}


@router.get("/{session_id}/context")
async def get_session_context(
    session_id: str,
    limit: int = 50,
    current_user: User = Depends(deps.get_current_user),
):
    try:
        return await session_service.get_session_context(
            session_id=session_id,
            user_id=str(current_user.id),
            limit=limit,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")


@router.post("/{session_id}/fork")
async def fork_session(
    session_id: str,
    current_user: User = Depends(deps.get_current_user),
):
    try:
        new_session = await session_service.fork_session(session_id=session_id, user_id=str(current_user.id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"forked_session_id": str(new_session.id)}


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(deps.get_current_user),
):
    deleted = await session_service.delete_session(session_id=session_id, user_id=str(current_user.id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted"}

