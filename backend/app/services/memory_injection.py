"""
Memory Injection Service for Agent OS v2.
Provides functionality to retrieve relevant past memories and inject them into LLM prompts.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..services.embedding_service import embed
from ..models.models import AgentMemory
from ..database import SessionLocal


async def inject_memory_context(
    user_id: str,
    query: str,
    agent_id: Optional[str] = None,
    limit: int = 3
) -> str:
    """
    Retrieve relevant memories and format as context string.

    Args:
        user_id: User UUID as string
        query: The query/prompt to search for relevant memories
        agent_id: Optional agent ID to filter memories by specific agent
        limit: Maximum number of memories to retrieve

    Returns:
        Formatted context string or empty string if no memories found
    """
    try:
        # Generate embedding for the query
        embedding = embed(query)

        # Build the SQL query
        sql = """
            SELECT content FROM agent_memories
            WHERE user_id = :user_id
        """
        params = {"user_id": user_id, "emb": str(embedding), "limit": limit}

        if agent_id:
            sql += " AND agent_id = :agent_id"
            params["agent_id"] = agent_id

        sql += """
            ORDER BY embedding <=> CAST(:emb AS vector)
            LIMIT :limit
        """

        # Execute the query
        with SessionLocal() as db:
            rows = db.execute(text(sql), params).fetchall()
            memories = [r[0] for r in rows]

        if not memories:
            return ""

        return "## Past relevant information\n" + "\n".join([f"- {m}" for m in memories])

    except Exception as e:
        # Fail gracefully - if memory injection fails, continue without context
        print(f"[Memory Injection] Warning: {e}")
        return ""