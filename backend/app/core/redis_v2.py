"""
Unified Redis Client with Multi-DB Pattern.

Supports: Cache, Session, Pub/Sub, Lock, Rate Limit, Agent Memory.
"""

from __future__ import annotations

import json
import pickle
from typing import Any, Optional

import redis.asyncio as aioredis

from app.core.config_v2 import settings


class RedisManager:
    """Manages multiple Redis connections for different purposes."""

    def __init__(self) -> None:
        self._pools: dict[int, aioredis.Redis] = {}
        self._prefix = "si:v2"

    def _get_url(self, db: int) -> str:
        base = settings.REDIS_URL.rstrip("/")
        return f"{base}/{db}"

    async def _get_client(self, db: int) -> aioredis.Redis:
        if db not in self._pools:
            self._pools[db] = aioredis.from_url(
                self._get_url(db),
                decode_responses=True,
                max_connections=50,
            )
        return self._pools[db]

    def _key(self, namespace: str, key: str) -> str:
        return f"{self._prefix}:{namespace}:{key}"

    # ── Cache Operations ─────────────────────────────────────────────────────
    async def cache_get(self, key: str) -> Optional[Any]:
        client = await self._get_client(settings.REDIS_DB_CACHE)
        data = await client.get(self._key("cache", key))
        return json.loads(data) if data else None

    async def cache_set(self, key: str, value: Any, ttl: int = 3600) -> None:
        client = await self._get_client(settings.REDIS_DB_CACHE)
        await client.setex(self._key("cache", key), ttl, json.dumps(value, default=str))

    async def cache_delete(self, key: str) -> None:
        client = await self._get_client(settings.REDIS_DB_CACHE)
        await client.delete(self._key("cache", key))

    # ── Session Operations ───────────────────────────────────────────────────
    async def session_get(self, session_id: str) -> Optional[dict]:
        client = await self._get_client(settings.REDIS_DB_SESSION)
        data = await client.get(self._key("session", session_id))
        return json.loads(data) if data else None

    async def session_set(self, session_id: str, data: dict, ttl: int | None = None) -> None:
        client = await self._get_client(settings.REDIS_DB_SESSION)
        ttl_seconds = ttl or settings.SESSION_TTL_SECONDS
        await client.setex(self._key("session", session_id), ttl_seconds, json.dumps(data, default=str))

    async def session_delete(self, session_id: str) -> None:
        client = await self._get_client(settings.REDIS_DB_SESSION)
        await client.delete(self._key("session", session_id))

    async def session_exists(self, session_id: str) -> bool:
        client = await self._get_client(settings.REDIS_DB_SESSION)
        return (await client.exists(self._key("session", session_id))) > 0

    # ── Pub/Sub ──────────────────────────────────────────────────────────────
    async def publish(self, channel: str, message: dict) -> None:
        client = await self._get_client(settings.REDIS_DB_PUBSUB)
        await client.publish(channel, json.dumps(message, default=str))

    async def subscribe(self, channel: str):
        client = await self._get_client(settings.REDIS_DB_PUBSUB)
        pubsub = client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    # ── Distributed Lock ─────────────────────────────────────────────────────
    async def acquire_lock(self, lock_name: str, timeout: int = 30) -> bool:
        client = await self._get_client(settings.REDIS_DB_LOCK)
        return bool(
            await client.set(self._key("lock", lock_name), "1", nx=True, ex=timeout),
        )

    async def release_lock(self, lock_name: str) -> None:
        client = await self._get_client(settings.REDIS_DB_LOCK)
        await client.delete(self._key("lock", lock_name))

    # ── Rate Limiting ────────────────────────────────────────────────────────
    async def rate_limit_check(self, key: str, max_requests: int, window: int) -> tuple[bool, int]:
        """Return (allowed, remaining) for a fixed window bucket."""

        client = await self._get_client(settings.REDIS_DB_RATE_LIMIT)

        now = await client.time()
        current_time = int(now[0])
        window_key = f"{self._key('ratelimit', key)}:{current_time // window}"

        pipe = client.pipeline()
        pipe.incr(window_key)
        pipe.expire(window_key, window)
        results = await pipe.execute()

        current_count = int(results[0])
        allowed = current_count <= max_requests
        remaining = max(0, max_requests - current_count)
        return allowed, remaining

    # ── Agent Memory ─────────────────────────────────────────────────────────
    async def agent_memory_get(self, agent_id: str, key: str) -> Optional[Any]:
        client = await self._get_client(settings.REDIS_DB_AGENT_MEMORY)
        data = await client.hget(self._key("agent", agent_id), key)
        if not data:
            return None
        return pickle.loads(data.encode("latin-1"))

    async def agent_memory_set(self, agent_id: str, key: str, value: Any) -> None:
        client = await self._get_client(settings.REDIS_DB_AGENT_MEMORY)
        await client.hset(
            self._key("agent", agent_id),
            key,
            pickle.dumps(value).decode("latin-1"),
        )
        await client.expire(self._key("agent", agent_id), settings.AGENT_MEMORY_TTL)

    async def agent_memory_clear(self, agent_id: str) -> None:
        client = await self._get_client(settings.REDIS_DB_AGENT_MEMORY)
        await client.delete(self._key("agent", agent_id))

    # ── Cleanup ──────────────────────────────────────────────────────────────
    async def close_all(self) -> None:
        for pool in self._pools.values():
            await pool.close()


redis_manager = RedisManager()


async def get_redis() -> RedisManager:
    """FastAPI dependency for the shared Redis manager."""

    return redis_manager

