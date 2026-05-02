"""
Cost Engine for Agent OS v2.

Manages per-mission-type cost limits and daily tracking.
Enforces spending caps for different mission categories.
"""

import time
from typing import Dict, Optional
from ..core.redis_client import r


def check_mission_cost(user_id: str, mission_type: str, estimated_cost: float) -> None:
    """
    Check if a user can afford a mission based on daily limits per mission type.

    Args:
        user_id: User UUID as string
        mission_type: Type of mission (e.g., "scout", "ammo_generation", "bounty_match")
        estimated_cost: Estimated cost of the mission

    Raises:
        Exception: If daily cost limit for mission type is exceeded
    """
    today = time.strftime("%Y%m%d")
    key = f"cost:{user_id}:{mission_type}:{today}"
    current = float(r.get(key) or 0.0)

    # Define daily limits per mission type
    limits: Dict[str, float] = {
        "scout": 0.10,
        "ammo_generation": 0.20,
        "bounty_match": 0.30,
        "hermes_planning": 0.15,
        "map_rendering": 0.05,
        "paperclip_generation": 0.25,
        "default": 0.10  # fallback for unknown mission types
    }

    limit = limits.get(mission_type, limits["default"])

    if current + estimated_cost > limit:
        raise Exception(
            f"Daily cost limit for {mission_type} exceeded: "
            f"{current:.3f} + {estimated_cost:.3f} > {limit:.3f}"
        )

    # Atomically increment cost
    r.incrbyfloat(key, estimated_cost)
    r.expire(key, 86400)  # 24 hours TTL


def get_mission_cost_today(user_id: str, mission_type: str) -> float:
    """
    Get today's total cost for a specific mission type.

    Args:
        user_id: User UUID as string
        mission_type: Type of mission

    Returns:
        Total cost spent today
    """
    today = time.strftime("%Y%m%d")
    key = f"cost:{user_id}:{mission_type}:{today}"
    cost = r.get(key)
    return float(cost) if cost else 0.0


def get_total_cost_today(user_id: str) -> Dict[str, float]:
    """
    Get all mission costs for a user today.

    Args:
        user_id: User UUID as string

    Returns:
        Dictionary mapping mission types to costs
    """
    today = time.strftime("%Y%m%d")
    pattern = f"cost:{user_id}:*:{today}"
    keys = r.keys(pattern)

    result = {}
    for key in keys:
        # Extract mission type from key pattern
        parts = key.split(":")
        if len(parts) >= 3:
            mission_type = parts[2]
            cost = float(r.get(key) or 0.0)
            if cost > 0:
                result[mission_type] = cost

    return result


def reset_mission_costs(user_id: Optional[str] = None) -> None:
    """
    Reset mission costs (for testing or admin purposes).

    Args:
        user_id: Optional user ID to reset costs for, or None for all users
    """
    if user_id:
        pattern = f"cost:{user_id}:*"
    else:
        pattern = "cost:*"

    keys = r.keys(pattern)
    if keys:
        r.delete(*keys)


def set_mission_limit(mission_type: str, limit: float) -> None:
    """
    Set a custom daily limit for a mission type (admin function).

    Args:
        mission_type: Type of mission
        limit: New daily limit
    """
    key = f"mission_limit:{mission_type}"
    r.set(key, limit)


def get_mission_limit(mission_type: str) -> float:
    """
    Get the daily limit for a mission type.

    Args:
        mission_type: Type of mission

    Returns:
        Daily limit (defaults based on built-in limits)
    """
    key = f"mission_limit:{mission_type}"
    limit = r.get(key)

    if limit:
        return float(limit)

    # Default limits
    defaults = {
        "scout": 0.10,
        "ammo_generation": 0.20,
        "bounty_match": 0.30,
        "hermes_planning": 0.15,
        "map_rendering": 0.05,
        "paperclip_generation": 0.25,
    }

    return defaults.get(mission_type, 0.10)