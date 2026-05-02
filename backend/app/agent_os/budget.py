"""
Budget System for Agent OS v2.

Provides atomic budget checking and cost tracking with Redis Lua scripts
to ensure thread-safe operations across distributed workers.
"""

from typing import Optional
from ..core.redis_client import r

# Lua script for atomic budget check and update
LUA_CHECK_BUDGET = """
local current = tonumber(redis.call('get', KEYS[1]) or '0')
local cost = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])
if current + cost > limit then
    return 0  -- budget exceeded
end
redis.call('incrbyfloat', KEYS[1], cost)
redis.call('expire', KEYS[1], 86400)  -- 24 hours TTL
return 1  -- budget allowed
"""


def check_budget(user_id: str, cost: float = 0.01, limit: float = 1.0) -> None:
    """
    Check if a user has sufficient budget for an operation.

    Args:
        user_id: User UUID as string
        cost: Cost of the operation (default: 0.01)
        limit: Daily budget limit (default: 1.0)

    Raises:
        Exception: If budget is exceeded
    """
    key = f"budget:{user_id}"
    allowed = r.eval(LUA_CHECK_BUDGET, 1, key, cost, limit)
    if allowed == 0:
        raise Exception(f"Budget exceeded: cost {cost} exceeds limit {limit}")


def add_cost(user_id: str, cost: float) -> None:
    """
    Add cost to a user's budget (alternative method).

    Args:
        user_id: User UUID as string
        cost: Cost to add (positive)
    """
    if cost <= 0:
        return

    key = f"budget:{user_id}"
    r.incrbyfloat(key, cost)
    r.expire(key, 86400)  # 24 hours TTL


def get_budget_usage(user_id: str) -> float:
    """
    Get current budget usage for a user.

    Args:
        user_id: User UUID as string

    Returns:
        Current usage amount
    """
    key = f"budget:{user_id}"
    usage = r.get(key)
    return float(usage) if usage else 0.0


def reset_budget(user_id: str) -> None:
    """
    Reset budget for a user (e.g., at start of new day).

    Args:
        user_id: User UUID as string
    """
    key = f"budget:{user_id}"
    r.delete(key)


def set_budget_limit(user_id: str, limit: float) -> None:
    """
    Set a custom budget limit for a user.

    Args:
        user_id: User UUID as string
        limit: New daily limit
    """
    key = f"budget_limit:{user_id}"
    r.setex(key, 86400, limit)


def get_budget_limit(user_id: str) -> float:
    """
    Get budget limit for a user.

    Args:
        user_id: User UUID as string

    Returns:
        Budget limit (defaults to 1.0 if not set)
    """
    key = f"budget_limit:{user_id}"
    limit = r.get(key)
    return float(limit) if limit else 1.0