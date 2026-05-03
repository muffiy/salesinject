"""
Unified Redis client for Agent OS v2.
Provides a single Redis connection for the entire application.
Falls back to a no-op stub if Redis is unavailable.
"""

import logging
import redis
from .config import settings

logger = logging.getLogger(__name__)


class _NoopRedis:
    """No-op Redis stub when Redis is unavailable."""
    def get(self, key): return None
    def set(self, key, value, **kwargs): return True
    def setex(self, key, time, value): return True
    def delete(self, *keys): return 0
    def exists(self, key): return 0
    def incr(self, key): return 1
    def decr(self, key): return 0
    def expire(self, key, seconds): return True
    def ttl(self, key): return -1
    def ping(self): return True
    def lpush(self, key, *values): return 1
    def lrange(self, key, start, end): return []
    def publish(self, channel, message): return 0
    def hget(self, name, key): return None
    def hset(self, name, key=None, value=None, mapping=None): return 1
    def hgetall(self, name): return {}
    def eval(self, script, numkeys, *keys_and_args): return 1
    def incrbyfloat(self, key, amount): return amount
    def keys(self, pattern): return []


def _make_redis():
    try:
        client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        client.ping()
        logger.info("Redis connected successfully")
        return client
    except Exception as e:
        logger.warning(f"Redis unavailable ({e}), using no-op stub")
        return _NoopRedis()


r = _make_redis()
