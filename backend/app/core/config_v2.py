"""
SalesInject Backend Configuration v2
Supports: Content Generation, Multi-Session, Agentic Core
"""

from __future__ import annotations

import os
import secrets
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Core App ──────────────────────────────────────────────────────────────
    PROJECT_NAME: str = "SalesInject"
    VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    ENV: str = os.getenv("ENV", "development")

    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY") or secrets.token_urlsafe(48)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    API_KEY_HEADER: str = "X-API-Key"

    # ── Database ──────────────────────────────────────────────────────────────
    # Note: URL uses asyncpg here; ensure DB layer matches (async SQLAlchemy) before switching to it.
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:password@localhost:5432/salesinject",
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_RECYCLE: int = 3600

    # ── Redis (Multi-DB Pattern) ──────────────────────────────────────────────
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_DB_CACHE: int = 0
    REDIS_DB_SESSION: int = 1
    REDIS_DB_PUBSUB: int = 2
    REDIS_DB_LOCK: int = 3
    REDIS_DB_RATE_LIMIT: int = 4
    REDIS_DB_AGENT_MEMORY: int = 5

    # ── Content Generation ────────────────────────────────────────────────────
    # Model Routing: cheap/fast → premium/slow
    CONTENT_MODEL_TIER_1: str = os.getenv("CONTENT_MODEL_TIER_1", "gpt-4o-mini")
    CONTENT_MODEL_TIER_2: str = os.getenv("CONTENT_MODEL_TIER_2", "gpt-4o")
    CONTENT_MODEL_TIER_3: str = os.getenv("CONTENT_MODEL_TIER_3", "claude-3-5-sonnet")

    # Generation Limits
    MAX_CONTENT_LENGTH: int = 4000
    DEFAULT_GENERATION_TIMEOUT: int = 60
    MAX_GENERATIONS_PER_HOUR: int = 100
    MAX_GENERATIONS_PER_DAY: int = 500

    # ── Multi-Session ─────────────────────────────────────────────────────────
    SESSION_TTL_SECONDS: int = 3600 * 24 * 7  # 7 days
    SESSION_MAX_BRANCHES: int = 10
    SESSION_MAX_MESSAGES: int = 100
    SESSION_CONTEXT_WINDOW: int = 10  # Last N messages for context

    # ── AI Agent ──────────────────────────────────────────────────────────────
    AGENT_MAX_STEPS: int = 10
    AGENT_MAX_TOOL_CALLS: int = 5
    AGENT_TIMEOUT_SECONDS: int = 120
    AGENT_MEMORY_TTL: int = 3600 * 24 * 30  # 30 days

    # ── External APIs ─────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    EXA_API_KEY: str = os.getenv("EXA_API_KEY", "")
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # ── Social APIs ───────────────────────────────────────────────────────────
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY", "")
    TWITTER_API_SECRET: str = os.getenv("TWITTER_API_SECRET", "")
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    TIKTOK_ACCESS_TOKEN: str = os.getenv("TIKTOK_ACCESS_TOKEN", "")
    LINKEDIN_ACCESS_TOKEN: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")

    # ── Telegram ──────────────────────────────────────────────────────────────
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    MINI_APP_URL: str = os.getenv("MINI_APP_URL", "")
    USE_WEBHOOK: bool = os.getenv("USE_WEBHOOK", "False").lower() in ("true", "1", "t")
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")

    # ── Storage ───────────────────────────────────────────────────────────────
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "salesinject-content")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")

    # ── Messaging ─────────────────────────────────────────────────────────────
    REDPANDA_BROKERS: str = os.getenv("REDPANDA_BROKERS", "redpanda:9092")

    # ── Platform ──────────────────────────────────────────────────────────────
    PLATFORM_COMMISSION_RATE: float = float(os.getenv("PLATFORM_COMMISSION_RATE", "0.10"))

    # ── Feature Flags ─────────────────────────────────────────────────────────
    ENABLE_AGENTIC_MODE: bool = os.getenv("ENABLE_AGENTIC_MODE", "False").lower() in ("true", "1", "t")
    ENABLE_SOCIAL_LISTENING: bool = os.getenv("ENABLE_SOCIAL_LISTENING", "False").lower() in ("true", "1", "t")
    ENABLE_AUTO_PUBLISH: bool = os.getenv("ENABLE_AUTO_PUBLISH", "False").lower() in ("true", "1", "t")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance for performance."""

    return Settings()


settings = get_settings()
