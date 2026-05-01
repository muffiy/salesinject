import redis
from app.core.config import settings

# Initialize Redis client for locking and caching
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis():
    """Dependency for retrieving the Redis client."""
    return redis_client
