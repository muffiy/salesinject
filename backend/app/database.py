# Re-export from core for backwards compat
from app.core.database import get_db, engine, SessionLocal

__all__ = ["get_db", "engine", "SessionLocal"]
