from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Date, BigInteger
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String)
    first_name = Column(String)
    role = Column(String, default="creator") # 'creator' or 'brand'
    niche_preferences = Column(ARRAY(String))
    wallet_balance = Column(Numeric(10, 2), default=0.0)
    rank = Column(String, default="bronze") # bronze, silver, gold
    total_earnings = Column(Numeric(10, 2), default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    agents = relationship("Agent", back_populates="owner")
    tasks = relationship("UserTask", back_populates="user")
    scores = relationship("Score", back_populates="user")
    payments = relationship("Payment", back_populates="user")

class Agent(Base):
    __tablename__ = "agents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String)
    niche = Column(String)
    configuration = Column(JSONB)
    performance_score = Column(Numeric(5, 2), default=0.0)
    tasks_completed = Column(Integer, default=0)
    total_earnings = Column(Numeric(10, 2), default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="agents")
    tasks = relationship("UserTask", back_populates="agent")
    memories = relationship("AgentMemory", back_populates="agent", cascade="all, delete")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    title = Column(String)
    description = Column(String)
    niche = Column(String)
    reward_amount = Column(Numeric(10, 2))
    deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="open") # open, in_progress, completed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_submissions = relationship("UserTask", back_populates="task")

class UserTask(Base):
    __tablename__ = "user_tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    submission_url = Column(String)
    status = Column(String, default="pending") # pending, approved, rejected
    approved_at = Column(DateTime(timezone=True), nullable=True)
    earnings = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="tasks")
    task = relationship("Task", back_populates="user_submissions")
    agent = relationship("Agent", back_populates="tasks")

class Ad(Base):
    __tablename__ = "ads"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String)
    ad_url = Column(String, unique=True)
    niche = Column(String)
    creative_text = Column(String)
    hooks = Column(ARRAY(String))
    engagement_data = Column(JSONB)
    embedding = Column(Vector(384))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

class AgentMemory(Base):
    __tablename__ = "agent_memories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    memory_type = Column(String)
    content = Column(String)
    embedding = Column(Vector(384))
    memory_metadata = Column("metadata", JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    agent = relationship("Agent", back_populates="memories")

class Score(Base):
    __tablename__ = "scores"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    period_start = Column(Date)
    period_end = Column(Date)
    tasks_completed = Column(Integer, default=0)
    earnings = Column(Numeric(10, 2), default=0.0)
    rank = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="scores")

class Conversion(Base):
    __tablename__ = "conversions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    revenue = Column(Numeric(10, 2))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    amount = Column(Numeric(10, 2))
    currency = Column(String, default="USD")
    status = Column(String, default="pending") # pending, completed, failed
    stripe_payment_intent_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="payments")

class ScoutReport(Base):
    __tablename__ = "scout_reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    target_niche = Column(String)
    map_data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PaperclipItem(Base):
    __tablename__ = "paperclip_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True) # Optional link to Task
    item_type = Column(String) # 'mission_log', 'pinned_profile', or 'ad_copy'
    content = Column(JSONB) # Storage for varied data payloads
    created_at = Column(DateTime(timezone=True), server_default=func.now())
