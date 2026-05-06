from pydantic_settings import BaseSettings
import os
import secrets

class Settings(BaseSettings):
    PROJECT_NAME: str = "SalesInject"
    SECRET_KEY: str = os.getenv("SECRET_KEY") or secrets.token_urlsafe(48)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes; refresh via /auth/refresh
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    OPENCLAW_URL: str = os.getenv("OPENCLAW_URL", "http://localhost:18789")
    EXA_API_KEY: str = os.getenv("EXA_API_KEY", "")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "dummy")
    MINI_APP_URL: str = os.getenv("MINI_APP_URL", "https://t.me/dummy")
    USE_WEBHOOK: bool = os.getenv("USE_WEBHOOK", "False").lower() in ("true", "1", "t")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/salesinject")
    REDPANDA_BROKERS: str = os.getenv("REDPANDA_BROKERS", "redpanda:9092")
    PLATFORM_COMMISSION_RATE: float = float(os.getenv("PLATFORM_COMMISSION_RATE", "0.10"))
    AGENT_OS_DEBUG: bool = os.getenv("AGENT_OS_DEBUG", "False").lower() in ("true", "1", "t")
    ALLOW_INSECURE_TG_INIT_DATA: bool = os.getenv("ALLOW_INSECURE_TG_INIT_DATA", "False").lower() in ("true", "1", "t")
    TELEGRAM_INITDATA_MAX_AGE_SECONDS: int = int(os.getenv("TELEGRAM_INITDATA_MAX_AGE_SECONDS", "86400"))

settings = Settings()
