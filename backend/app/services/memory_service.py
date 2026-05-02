"""
Memory Service for Agent OS v2.

Manages agent sessions, memories, and messages with scoped isolation.
Provides clean session lifecycle and memory persistence.
"""

import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from ..models_agent_os import AgentSession, AgentMessage, AgentMemory
from ..database import SessionLocal
from ..core.redis_client import r


def get_or_create_session(user_id: str, agent_type: str) -> str:
    """
    Get an existing active session or create a new one for the user and agent type.

    Args:
        user_id: User UUID as string
        agent_type: Type of agent (e.g., "scout", "hermes", "paperclip")

    Returns:
        Session ID as string
    """
    with SessionLocal() as db:
        # Look for active sessions first
        session = db.query(AgentSession).filter_by(
            user_id=user_id,
            agent_type=agent_type,
            status="active"
        ).order_by(AgentSession.created_at.desc()).first()

        if not session:
            # Create new session
            session = AgentSession(
                user_id=user_id,
                agent_type=agent_type,
                status="active"
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        return str(session.id)


def save_memory(
    user_id: str,
    session_id: str,
    agent_type: str,
    memory_type: str,
    content: Any,
    embedding: Optional[List[float]] = None
) -> str:
    """
    Save a memory entry for an agent session.

    Args:
        user_id: User UUID as string
        session_id: Session UUID as string
        agent_type: Type of agent
        memory_type: Type of memory (e.g., "identity", "mission_result", "context")
        content: Memory content (will be serialized to JSON)
        embedding: Optional vector embedding

    Returns:
        Memory ID as string
    """
    with SessionLocal() as db:
        memory = AgentMemory(
            user_id=user_id,
            session_id=session_id,
            agent_type=agent_type,
            memory_type=memory_type,
            content=json.dumps(content) if not isinstance(content, str) else content,
            embedding=embedding
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return str(memory.id)


def save_message(user_id: str, session_id: str, role: str, content: str) -> str:
    """
    Save a conversation message within an agent session.

    Args:
        user_id: User UUID as string
        session_id: Session UUID as string
        role: Message role ("user", "agent", "system")
        content: Message content

    Returns:
        Message ID as string
    """
    with SessionLocal() as db:
        message = AgentMessage(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return str(message.id)


def load_identity(user_id: str) -> dict:
    """
    Load the identity memory for a user.

    Args:
        user_id: User UUID as string

    Returns:
        Identity dictionary or empty dict if not found
    """
    with SessionLocal() as db:
        memory = db.query(AgentMemory).filter_by(
            user_id=user_id,
            memory_type='identity'
        ).order_by(AgentMemory.created_at.desc()).first()

        if memory:
            try:
                return json.loads(memory.content)
            except (json.JSONDecodeError, TypeError):
                return {"raw": memory.content}
        return {}


def load_session_messages(user_id: str, session_id: str, limit: int = 20) -> List[Dict[str, str]]:
    """
    Load conversation messages for a session.

    Args:
        user_id: User UUID as string
        session_id: Session UUID as string
        limit: Maximum number of messages to load

    Returns:
        List of message dictionaries with role and content
    """
    with SessionLocal() as db:
        messages = db.query(AgentMessage).filter_by(
            user_id=user_id,
            session_id=session_id
        ).order_by(AgentMessage.created_at.asc()).limit(limit).all()

        return [{"role": msg.role, "content": msg.content} for msg in messages]


def load_session_memories(
    user_id: str,
    session_id: str,
    memory_type: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Load memories for a session, optionally filtered by type.

    Args:
        user_id: User UUID as string
        session_id: Session UUID as string
        memory_type: Optional filter by memory type
        limit: Maximum number of memories to load

    Returns:
        List of memory dictionaries
    """
    with SessionLocal() as db:
        query = db.query(AgentMemory).filter_by(
            user_id=user_id,
            session_id=session_id
        )

        if memory_type:
            query = query.filter_by(memory_type=memory_type)

        memories = query.order_by(AgentMemory.created_at.desc()).limit(limit).all()

        result = []
        for memory in memories:
            content = memory.content
            try:
                content = json.loads(content)
            except (json.JSONDecodeError, TypeError):
                pass

            result.append({
                "id": str(memory.id),
                "memory_type": memory.memory_type,
                "content": content,
                "created_at": memory.created_at.isoformat() if memory.created_at else None
            })

        return result


def complete_session(session_id: str, status: str = "completed") -> bool:
    """
    Mark a session as completed or failed.

    Args:
        session_id: Session UUID as string
        status: Final status ("completed" or "failed")

    Returns:
        True if successful, False if session not found
    """
    with SessionLocal() as db:
        session = db.query(AgentSession).filter_by(id=session_id).first()
        if not session:
            return False

        session.status = status
        session.completed_at = func.now()
        db.commit()
        return True