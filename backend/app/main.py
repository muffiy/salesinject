from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
import asyncio
from aiogram import types as tg_types

from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from . import models
from .database import engine, SessionLocal
from .api.v1.router import api_router
from .routers import agent, seed
from .core.config import settings
from .bot.agent import bot, dp

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.USE_WEBHOOK:
        # In a real environment, set webhook URL here if not managed out-of-band:
        # await bot.set_webhook(url=f"https://your.prod.url/webhook/telegram")
        pass
    else:
        # Start long-polling
        asyncio.create_task(dp.start_polling(bot))
    yield
    await bot.session.close()

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="SalesInject API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── RLS Session Middleware ────────────────────────────────────────────────────
class RLSSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
                )
                user_id = payload.get("user_id")
                if user_id:
                    db = SessionLocal()
                    try:
                        db.execute(text(f"SET app.current_user_id = '{user_id}'"))
                        db.commit()
                    finally:
                        db.close()
            except Exception:
                pass
        response = await call_next(request)
        return response

app.add_middleware(RLSSessionMiddleware)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")
app.include_router(agent.router)
app.include_router(seed.router)

@app.get("/")
def read_root():
    return {"status": "ok", "app": "SalesInject API"}

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    if not settings.USE_WEBHOOK:
        return {"error": "Webhook not enabled"}
    
    update = tg_types.Update(**await request.json())
    await dp.feed_update(bot=bot, update=update)
    return {"status": "ok"}


# ── RLS Debug Endpoint (dev only) ────────────────────────────────────────────
if settings.DEBUG:
    from .api import deps as _deps
    from sqlalchemy import text as _text

    @app.get("/api/v1/debug/rls")
    def debug_rls(
        current_user=Depends(_deps.get_current_user),
        db: SessionLocal = Depends(_deps.get_db),  # type: ignore[valid-type]
    ):
        result = db.execute(_text("SELECT current_setting('app.current_user_id', true)")).scalar()
        return {
            "jwt_user_id": str(current_user.id),
            "pg_session_user_id": result,
            "match": str(current_user.id) == (result or ""),
        }
