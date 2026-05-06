"""
Session Service v2

Multi-session support with branching, resumption, and context retrieval.
Uses the async DB layer (`database_v2`) and Redis session cache (`redis_v2`).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import delete, select, update

from app.core.config_v2 import settings
from app.core.database_v2 import AsyncSessionLocal
from app.core.redis_v2 import redis_manager
from app.models import AgentMemory, AgentMessage, AgentSession


def _to_uuid(value: str) -> uuid.UUID:
    return uuid.UUID(value)


class SessionService:
    def __init__(self) -> None:
        self.redis = redis_manager

    async def create_session(
        self,
        *,
        user_id: str,
        agent_type: str,
        parent_session_id: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> AgentSession:
        parent_uuid: uuid.UUID | None = _to_uuid(parent_session_id) if parent_session_id else None
        user_uuid = _to_uuid(user_id)

        async with AsyncSessionLocal() as db:
            if parent_uuid:
                parent = await db.scalar(
                    select(AgentSession).where(AgentSession.id == parent_uuid, AgentSession.user_id == user_uuid),
                )
                if not parent:
                    raise ValueError("Parent session not found or not owned by user")

            session = AgentSession(
                id=uuid.uuid4(),
                user_id=user_uuid,
                agent_type=agent_type,
                parent_session_id=parent_uuid,
                status="active",
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)

            if parent_uuid:
                await self._copy_context_from_parent(
                    parent_id=parent_uuid,
                    child_id=session.id,
                    user_id=user_uuid,
                )

            cache_payload: dict[str, Any] = {
                "id": str(session.id),
                "user_id": str(session.user_id),
                "agent_type": session.agent_type,
                "parent_session_id": str(session.parent_session_id) if session.parent_session_id else None,
                "status": session.status,
                "created_at": (session.created_at.isoformat() if session.created_at else datetime.now(timezone.utc).isoformat()),
            }
            if context:
                cache_payload["context"] = context

            await self.redis.session_set(str(session.id), cache_payload, ttl=settings.SESSION_TTL_SECONDS)
            return session

    async def get_session(self, *, session_id: str) -> Optional[dict[str, Any]]:
        cached = await self.redis.session_get(session_id)
        if cached:
            return cached

        session_uuid = _to_uuid(session_id)
        async with AsyncSessionLocal() as db:
            session = await db.scalar(select(AgentSession).where(AgentSession.id == session_uuid))
            if not session:
                return None

            payload = {
                "id": str(session.id),
                "user_id": str(session.user_id),
                "agent_type": session.agent_type,
                "parent_session_id": str(session.parent_session_id) if session.parent_session_id else None,
                "status": session.status,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            }
            await self.redis.session_set(session_id, payload, ttl=settings.SESSION_TTL_SECONDS)
            return payload

    async def resume_session(
        self,
        *,
        session_id: str,
        user_id: str,
        resume_context: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        session_uuid = _to_uuid(session_id)
        user_uuid = _to_uuid(user_id)

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                update(AgentSession)
                .where(AgentSession.id == session_uuid, AgentSession.user_id == user_uuid)
                .values(status="active", completed_at=None),
            )
            await db.commit()
            if result.rowcount == 0:
                return None

        session = await self.get_session(session_id=session_id)
        if not session:
            return None

        if resume_context:
            session["resume_context"] = resume_context
            session["resumed_at"] = datetime.now(timezone.utc).isoformat()
            await self.redis.session_set(session_id, session, ttl=settings.SESSION_TTL_SECONDS)

        return session

    async def get_session_context(self, *, session_id: str, user_id: str, limit: int = 50) -> dict[str, Any]:
        session = await self.get_session(session_id=session_id)
        if not session or session.get("user_id") != user_id:
            raise ValueError("Session not found or not owned by user")

        session_uuid = _to_uuid(session_id)
        user_uuid = _to_uuid(user_id)

        context: dict[str, Any] = {"messages": [], "memories": [], "artifacts": []}

        async with AsyncSessionLocal() as db:
            msg_result = await db.execute(
                select(AgentMessage)
                .where(AgentMessage.session_id == session_uuid, AgentMessage.user_id == user_uuid)
                .order_by(AgentMessage.created_at.asc())
                .limit(limit),
            )
            context["messages"] = [
                {
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in msg_result.scalars().all()
            ]

            # AgentMemory currently has no explicit session_id column in the schema.
            # We surface (a) identity memories, and (b) any memories tagged with session_id in JSONB metadata.
            mem_result = await db.execute(
                select(AgentMemory)
                .where(
                    AgentMemory.user_id == user_uuid,
                    (
                        (AgentMemory.memory_type == "identity")
                        | (AgentMemory.metadata_["session_id"].as_string() == str(session_uuid))
                    ),
                )
                .order_by(AgentMemory.created_at.desc())
                .limit(limit),
            )
            context["memories"] = [
                {
                    "type": m.memory_type,
                    "content": m.content,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                    "metadata": m.metadata_ or {},
                }
                for m in mem_result.scalars().all()
            ]

        return context

    async def fork_session(self, *, session_id: str, user_id: str) -> AgentSession:
        existing = await self.get_session(session_id=session_id)
        if not existing or existing.get("user_id") != user_id:
            raise ValueError("Session not found or not owned by user")

        return await self.create_session(
            user_id=user_id,
            agent_type=str(existing.get("agent_type") or "agent"),
            parent_session_id=session_id,
        )

    async def delete_session(self, *, session_id: str, user_id: str) -> bool:
        session_uuid = _to_uuid(session_id)
        user_uuid = _to_uuid(user_id)

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                delete(AgentSession).where(AgentSession.id == session_uuid, AgentSession.user_id == user_uuid),
            )
            await db.commit()

        await self.redis.session_delete(session_id)
        return (result.rowcount or 0) > 0

    async def _copy_context_from_parent(self, *, parent_id: uuid.UUID, child_id: uuid.UUID, user_id: uuid.UUID) -> None:
        async with AsyncSessionLocal() as db:
            msg_result = await db.execute(
                select(AgentMessage)
                .where(AgentMessage.session_id == parent_id, AgentMessage.user_id == user_id)
                .order_by(AgentMessage.created_at.desc())
                .limit(settings.SESSION_CONTEXT_WINDOW),
            )
            parent_messages = msg_result.scalars().all()

            for msg in reversed(parent_messages):
                db.add(
                    AgentMessage(
                        id=uuid.uuid4(),
                        user_id=user_id,
                        session_id=child_id,
                        role=msg.role,
                        content=msg.content,
                        created_at=datetime.now(timezone.utc),
                    ),
                )

            await db.commit()


session_service = SessionService()
