"""
Concurrency Limiter for Agent OS v2.

Manages concurrent mission execution per user to prevent resource exhaustion.
"""

from typing import Optional
from ..core.redis_client import r


def check_concurrency(user_id: str, max_active: int = 2) -> None:
    """
    Check if a user can start a new mission based on concurrency limit.

    Args:
        user_id: User UUID as string
        max_active: Maximum allowed active missions (default: 2)

    Raises:
        Exception: If user has too many active missions
    """
    key = f"active_missions:{user_id}"
    count = int(r.get(key) or 0)
    if count >= max_active:
        raise Exception(f"Too many active missions: {count}/{max_active}")


def increment_active(user_id: str) -> None:
    """
    Increment active mission count for a user.

    Args:
        user_id: User UUID as string
    """
    key = f"active_missions:{user_id}"
    r.incr(key)
    r.expire(key, 300)  # 5 minutes TTL, auto-cleanup if cleanup fails


def decrement_active(user_id: str) -> None:
    """
    Decrement active mission count for a user.

    Args:
        user_id: User UUID as string
    """
    key = f"active_missions:{user_id}"
    current = int(r.get(key) or 0)
    if current > 0:
        r.decr(key)


def get_active_count(user_id: str) -> int:
    """
    Get current number of active missions for a user.

    Args:
        user_id: User UUID as string

    Returns:
        Number of active missions
    """
    key = f"active_missions:{user_id}"
    count = r.get(key)
    return int(count) if count else 0


def set_concurrency_limit(user_id: Optional[str] = None, limit: int = 2) -> None:
    """
    Set custom concurrency limit (admin function).

    Args:
        user_id: Optional user ID to set limit for, or None for global default
        limit: New concurrency limit
    """
    if user_id:
        key = f"concurrency_limit:{user_id}"
    else:
        key = "concurrency_limit:global"

    r.set(key, limit)


def get_concurrency_limit(user_id: Optional[str] = None) -> int:
    """
    Get concurrency limit for a user or global default.

    Args:
        user_id: Optional user ID to get limit for

    Returns:
        Concurrency limit (defaults to 2)
    """
    if user_id:
        key = f"concurrency_limit:{user_id}"
        limit = r.get(key)
        if limit:
            return int(limit)

    # Check global default
    global_key = "concurrency_limit:global"
    global_limit = r.get(global_key)
    if global_limit:
        return int(global_limit)

    return 2  # Hard-coded default


def cleanup_stale_counts() -> None:
    """
    Clean up potentially stale active mission counts.

    This should be called periodically (e.g., by Celery Beat) to clean up
    counts that weren't properly decremented due to worker crashes.
    """
    pattern = "active_missions:*"
    keys = r.keys(pattern)
    for key in keys:
        # Remove keys with very old TTL (or implement more sophisticated cleanup)
        ttl = r.ttl(key)
        if ttl == -2:  # Key doesn't exist
            continue
        if ttl == -1:  # No TTL set (shouldn't happen with our code)
            r.delete(key)
        # Otherwise, let it expire naturally