from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Core
    DEBUG: bool = False
    SECRET_KEY: str = "CHANGE_ME"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Database
    DATABASE_URL: str = "postgresql://salesinject:password@localhost:5432/salesinject"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Telegram
    BOT_TOKEN: str = ""
    MINI_APP_URL: str = "http://localhost:5173"
    USE_WEBHOOK: bool = False
    WEBHOOK_URL: str = ""

    # AI / LLM
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "meta-llama/llama-3.1-8b-instruct:free"
    OPENAI_API_KEY: str = ""  # Legacy fallback
    EXA_API_KEY: str = ""

    # Commission
    PLATFORM_COMMISSION_RATE: float = 0.15  # 15%

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
