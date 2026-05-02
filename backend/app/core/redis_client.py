"""
Unified Redis client for Agent OS v2.
Provides a single Redis connection for the entire application.
"""

import redis
from .config import settings

# Create a global Redis client
r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)