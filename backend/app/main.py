from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.logging import setup_logging, StructuredLoggingMiddleware
from app.api.middleware.auth import ApiKeyAuthMiddleware
from app.core.metrics import PrometheusMiddleware, metrics_endpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start Telegram bot polling on startup, clean up on shutdown."""
    from app.bot import start_bot, stop_bot
    await start_bot()
    yield
    await stop_bot()


app = FastAPI(
    title="SalesInject API",
    description="AI-powered influencer marketing platform — The Visibility War Game",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(StructuredLoggingMiddleware)
setup_logging()

# Only enable API key auth when INTERNAL_API_KEY is configured
if os.environ.get("INTERNAL_API_KEY", ""):
    app.add_middleware(ApiKeyAuthMiddleware)

app.add_middleware(PrometheusMiddleware)

# Sentry error tracking (only when SENTRY_DSN is configured)
if settings.SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment="production" if not settings.DEBUG else "development",
        traces_sample_rate=0.1,
    )

# Health check at root level (nginx proxies /health here)
@app.get("/health")
def root_health():
    return {"status": "ok", "app": "salesinject"}

# Mount all v1 API routes
from app.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")

# Metrics endpoint (Prometheus)
app.add_route("/metrics", metrics_endpoint)
