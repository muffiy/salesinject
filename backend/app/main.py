from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check at root level (nginx proxies /health here)
@app.get("/health")
def root_health():
    return {"status": "ok", "app": "salesinject"}

# Mount all v1 API routes
from app.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")
