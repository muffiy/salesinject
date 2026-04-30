from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, agents, tasks, scout, offers, health, telegram

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(scout.router, prefix="/scout", tags=["Scout"])
api_router.include_router(offers.router, prefix="/offers", tags=["Offers"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["Telegram"])
