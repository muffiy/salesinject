import uuid
from sqlalchemy import Column, String, Integer, Float, Numeric, DateTime, ForeignKey, BigInteger, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    role = Column(String, default="creator")  # 'creator' or 'brand'
    niche_preferences = Column(ARRAY(String), default=[])
    wallet_balance = Column(Numeric(10, 2), default=0.0)
    rank = Column(String, default="bronze")  # bronze, silver, gold, diamond
    total_earnings = Column(Numeric(10, 2), default=0.0)
    streak_days = Column(Integer, default=0)
    last_active = Column(DateTime(timezone=True), server_default=func.now())
    onboarded = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    auto_boost = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reputation_score = Column(Integer, default=0)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)

    # Relationships
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")
    tasks_created = relationship("Task", back_populates="brand", foreign_keys="Task.brand_id")
    submissions = relationship("UserTask", back_populates="user")
    payments = relationship("PayoutTransaction", back_populates="user")
    scout_reports = relationship("ScoutReport", back_populates="user")
    paperclip_items = relationship("PaperclipItem", back_populates="user")


class Agent(Base):
    """AI agent instance owned by a user — Scout, Matchmaker, Content Gen."""
    __tablename__ = "agents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False, default="Scout Agent")
    niche = Column(String, nullable=True)
    agent_type = Column(String, default="scout")  # scout, matchmaker, content_gen
    configuration = Column(JSONB, default={})
    performance_score = Column(Float, default=0.0)
    tasks_completed = Column(Integer, default=0)
    total_earnings = Column(Numeric(10, 2), default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="agents")


class AgentSession(Base):
    __tablename__ = "agent_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    agent_type = Column(String, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class AgentMessage(Base):
    __tablename__ = "agent_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("agent_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AgentMemory(Base):
    __tablename__ = "agent_memories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=True)
    memory_type = Column(String)  # context, learning, preference
    content = Column(Text)
    embedding = Column(Vector(384))
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Task(Base):
    """Brand-created task/campaign that influencers can claim."""
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    niche = Column(String, nullable=True)
    reward_amount = Column(Numeric(10, 2), default=0.0)
    status = Column(String, default="open")  # open, in_progress, completed, expired
    max_claims = Column(Integer, default=10)
    deadline = Column(DateTime(timezone=True), nullable=True)
    requirements = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    brand = relationship("User", back_populates="tasks_created", foreign_keys=[brand_id])
    submissions = relationship("UserTask", back_populates="task")


class UserTask(Base):
    """Junction: an influencer's submission for a task."""
    __tablename__ = "user_tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    status = Column(String, default="pending")  # pending, submitted, approved, rejected
    submission_url = Column(String, nullable=True)
    earnings = Column(Numeric(10, 2), default=0.0)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="submissions")
    task = relationship("Task", back_populates="submissions")


class ScoutReport(Base):
    """Result of a scout mission — stores map_data for DeckGL rendering."""
    __tablename__ = "scout_reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_niche = Column(String, nullable=True)
    target_location = Column(String, nullable=True)
    map_data = Column(JSONB, default=[])  # Array of {lat, lon, name, followers, ...}
    report_text = Column(Text, nullable=True)
    influencer_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="scout_reports")


class PaperclipItem(Base):
    __tablename__ = "paperclip_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    item_type = Column(String)  # mission_log, pinned_profile, ad_copy, content_idea
    content = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="paperclip_items")


class Job(Base):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text)
    reward_amount = Column(Numeric(10, 2))
    status = Column(String, default="open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Offer(Base):
    """Location-based offer pinned on the map by a brand."""
    __tablename__ = "offers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    lat = Column(Numeric(9, 6), nullable=False)
    lon = Column(Numeric(9, 6), nullable=False)
    discount_value = Column(Numeric(10, 2), default=0.0)
    bounty_value = Column(Numeric(10, 2), default=0.0)
    promo_code = Column(String, nullable=True, unique=True)
    max_claims = Column(Integer, default=50)
    current_claims = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="active")  # active, expired, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    claims = relationship("OfferClaim", back_populates="offer")


class OfferClaim(Base):
    __tablename__ = "offer_claims"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    offer_id = Column(UUID(as_uuid=True), ForeignKey("offers.id", ondelete="CASCADE"))
    influencer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(String, default="claimed")  # claimed, pending_review, completed, rejected
    proof_url = Column(String, nullable=True)
    unique_code = Column(String, nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    claimed_at = Column(DateTime(timezone=True), server_default=func.now())
    position = Column(Integer, nullable=True)
    boosted = Column(Boolean, default=False)
    payout_amount = Column(Numeric(10, 2), default=0.0)

    offer = relationship("Offer", back_populates="claims")
    performance = relationship("OfferPerformance", back_populates="claim", uselist=False)


class OfferPerformance(Base):
    __tablename__ = "offer_performances"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("offer_claims.id", ondelete="CASCADE"))
    views = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    generated_revenue = Column(Numeric(10, 2), default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    claim = relationship("OfferClaim", back_populates="performance")


class PayoutTransaction(Base):
    __tablename__ = "payout_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    claim_id = Column(UUID(as_uuid=True), ForeignKey("offer_claims.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="TND")
    status = Column(String, default="pending")  # pending, processing, completed, failed
    payment_method = Column(String, nullable=True)  # flouci, d17, bank_transfer
    reference = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="payments")


class Leaderboard(Base):
    """Cached leaderboard for gamification — rebuilt periodically."""
    __tablename__ = "leaderboard"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    username = Column(String, nullable=True)
    score = Column(Float, default=0.0)
    rank_position = Column(Integer, default=0)
    offers_completed = Column(Integer, default=0)
    total_earned = Column(Numeric(10, 2), default=0.0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MissionShare(Base):
    __tablename__ = "mission_shares"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("offer_claims.id", ondelete="CASCADE"), nullable=False)
    bonus_granted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
