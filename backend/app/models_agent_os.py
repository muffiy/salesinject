"""
Agent OS v2 Database Models.
Only defines tables NOT already present in models/models.py.
"""

from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .models.models import Base


class AgentRanking(Base):
    """Agent performance rankings for market economy."""
    __tablename__ = "agent_rankings"

    agent_name = Column(String, primary_key=True)
    success_rate = Column(Float, default=0.5)
    avg_speed_ms = Column(Float, default=100.0)
    stake = Column(Float, default=0.0)
    failure_rate = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AgentStake(Base):
    """User stakes on agents in the market economy."""
    __tablename__ = "agent_stakes"

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    agent_name = Column(String, primary_key=True)
    amount = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
