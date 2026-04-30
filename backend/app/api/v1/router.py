from fastapi import APIRouter

from .endpoints import agents, auth, telegram, users, tasks, scout, health

api_router = APIRouter()
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["Telegram"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(scout.router, prefix="/scout", tags=["Scout"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
