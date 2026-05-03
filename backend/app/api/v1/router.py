from fastapi import APIRouter

from .endpoints import agents, auth, telegram, users, tasks, scout, health, offers, missions, earnings
from .ws import scout as ws_scout, stream, telemetry, live

api_router = APIRouter()
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["Telegram"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(scout.router, prefix="/scout", tags=["Scout"])
api_router.include_router(offers.router, prefix="/offers", tags=["Offers"])
api_router.include_router(missions.router, prefix="/missions", tags=["Missions"])
api_router.include_router(earnings.router, prefix="/earnings", tags=["Earnings"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])

# WebSocket routes (no prefix)
api_router.include_router(ws_scout.router, tags=["WebSocket"])
api_router.include_router(stream.router, tags=["WebSocket"])
api_router.include_router(telemetry.router, tags=["WebSocket"])
api_router.include_router(live.router, tags=["WebSocket"])
