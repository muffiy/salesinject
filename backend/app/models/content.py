from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.sql import func

from .models import Base


class BrandVoice(Base):
    __tablename__ = "brand_voices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    personality = Column(Text, nullable=True)
    writing_style = Column(Text, nullable=True)
    forbidden_words = Column(ARRAY(String), default=[])
    preferred_phrases = Column(ARRAY(String), default=[])
    emoji_style = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ContentTemplate(Base):
    __tablename__ = "content_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=True)
    content_type = Column(String, nullable=True)
    structure = Column(Text, nullable=False)
    variables = Column(ARRAY(String), default=[])

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ContentPiece(Base):
    __tablename__ = "content_pieces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    content_type = Column(String, nullable=False, default="social_post")
    prompt = Column(Text, nullable=False)
    raw_output = Column(JSONB, default={})
    parsed_content = Column(JSONB, default={})

    brand_voice_id = Column(UUID(as_uuid=True), ForeignKey("brand_voices.id", ondelete="SET NULL"), nullable=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("content_templates.id", ondelete="SET NULL"), nullable=True)

    model_used = Column(String, nullable=True)
    tokens_used = Column(Integer, default=0)
    metadata = Column(JSONB, default={})

    created_at = Column(DateTime(timezone=True), server_default=func.now())

