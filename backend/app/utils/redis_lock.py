import json
import redis
from app.core.config import settings

r = redis.Redis.from_url(settings.REDIS_URL)
LOCK_TTL = 120


def acquire_scout_lock(user_id: str, niche: str, location: str) -> dict | None:
    lock_key = f"scout:{user_id}:{niche}:{location}"
    acquired = r.set(lock_key, json.dumps({"status": "pending"}), nx=True, ex=LOCK_TTL)
    if not acquired:
        existing = r.get(lock_key)
        if existing:
            return json.loads(existing)
        return None
    return None


def update_lock_with_task_id(lock_key: str, task_id: str):
    r.set(lock_key, json.dumps({"task_id": task_id, "status": "running"}), ex=LOCK_TTL)


def release_lock(lock_key: str):
    r.delete(lock_key)