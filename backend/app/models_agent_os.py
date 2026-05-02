"""
Agent OS v2 Database Models.
Extends the main models.py with agent-specific tables.
"""

from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from .database import Base


class AgentSession(Base):
    """Agent session tracking for memory isolation."""
    __tablename__ = "agent_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    agent_type = Column(String)  # e.g., "scout", "hermes", "paperclip"
    status = Column(String, default="active")  # active, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    messages = relationship("AgentMessage", back_populates="session", cascade="all, delete-orphan")
    memories = relationship("AgentMemory", back_populates="session", cascade="all, delete-orphan")


class AgentMessage(Base):
    """Agent conversation messages within a session."""
    __tablename__ = "agent_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("agent_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String)  # user, agent, system
    content = Column(Text)
    metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("AgentSession", back_populates="messages")


class AgentRanking(Base):
    """Agent performance rankings for market economy."""
    __tablename__ = "agent_rankings"

    agent_name = Column(String, primary_key=True)  # e.g., "scout_collect", "hermes_plan"
    success_rate = Column(Float, default=0.5)  # 0.0 to 1.0
    avg_speed_ms = Column(Float, default=100.0)  # milliseconds
    stake = Column(Float, default=0.0)  # total stake amount
    failure_rate = Column(Float, default=0.0)  # 0.0 to 1.0
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AgentStake(Base):
    """User stakes on agents in the market economy."""
    __tablename__ = "agent_stakes"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    agent_name = Column(String, primary_key=True)  # matches agent_rankings.agent_name
    amount = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Update existing AgentMemory model to include session relationship
# Note: AgentMemory already exists in models.py, we're extending it
# We need to modify the existing class through a migration

# Placeholder for extended AgentMemory model
# This will be handled via Alembic migration to add session_id foreign key