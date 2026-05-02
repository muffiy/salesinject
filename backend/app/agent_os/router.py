"""
Node Router for Agent OS v2.

Routes workflow nodes to dedicated Celery queues based on node type.
Enables domain isolation and specialized worker clusters.
"""

from typing import Optional, Dict

# Node-to-queue routing table
NODE_ROUTING: Dict[str, str] = {
    # Scout domain
    "scout_collect": "scout",
    "scout_rank": "scout",
    "scout_analyze": "scout",

    # Core domain (Hermes planning/strategy)
    "hermes_plan": "core",
    "hermes_strategy": "core",
    "hermes_negotiation": "core",

    # Ammo domain (content generation)
    "paperclip_generate": "ammo",
    "ammo_validator": "ammo",
    "content_enhance": "ammo",

    # Bounty domain (matching and contracts)
    "matchmaker_agent": "bounty",
    "contract_builder": "bounty",
    "bounty_analyze": "bounty",

    # Fast domain (low-latency operations)
    "map_render": "fast",
    "notification_send": "fast",
    "cache_warm": "fast",

    # Fallback
    "default": "core"
}


def get_queue_for_node(node_name: str, region: Optional[str] = None) -> str:
    """
    Get Celery queue for a workflow node.

    Args:
        node_name: Name of the workflow node
        region: Optional region for multi-region support

    Returns:
        Celery queue name
    """
    queue = NODE_ROUTING.get(node_name, NODE_ROUTING["default"])

    # Add region suffix for multi-region support
    if region and region in ["af", "eu", "as", "us"]:
        return f"{queue}_{region}"

    return queue


def get_node_domain(node_name: str) -> str:
    """
    Get the domain/category of a node.

    Args:
        node_name: Name of the workflow node

    Returns:
        Domain name (scout, core, ammo, bounty, fast)
    """
    queue = get_queue_for_node(node_name)
    # Remove region suffix if present
    if "_" in queue:
        queue = queue.split("_")[0]
    return queue


def get_all_queues() -> Dict[str, list]:
    """
    Get all queues and their associated nodes.

    Returns:
        Dictionary mapping queue names to lists of node names
    """
    queues: Dict[str, list] = {}

    for node, queue in NODE_ROUTING.items():
        if node == "default":
            continue

        if queue not in queues:
            queues[queue] = []
        queues[queue].append(node)

    return queues


def validate_node(node_name: str) -> bool:
    """
    Validate if a node name exists in routing table.

    Args:
        node_name: Name of the workflow node

    Returns:
        True if node exists, False otherwise
    """
    return node_name in NODE_ROUTING


def register_node(node_name: str, queue: str) -> None:
    """
    Register a new node in routing table (runtime registration).

    Args:
        node_name: Name of the workflow node
        queue: Celery queue name
    """
    if node_name in NODE_ROUTING and node_name != "default":
        raise ValueError(f"Node '{node_name}' already registered")

    NODE_ROUTING[node_name] = queue


def unregister_node(node_name: str) -> None:
    """
    Unregister a node from routing table.

    Args:
        node_name: Name of the workflow node
    """
    if node_name not in NODE_ROUTING or node_name == "default":
        raise ValueError(f"Node '{node_name}' not registered or is default")

    del NODE_ROUTING[node_name]


# Utility for multi-region configuration
REGION_CONFIG = {
    "af": {"location": "Africa", "queues": ["scout_af", "core_af", "ammo_af"]},
    "eu": {"location": "Europe", "queues": ["scout_eu", "core_eu", "ammo_eu", "bounty_eu"]},
    "as": {"location": "Asia", "queues": ["scout_as", "core_as", "ammo_as"]},
    "us": {"location": "Americas", "queues": ["scout_us", "core_us", "ammo_us", "bounty_us", "fast_us"]},
}


def get_region_queues(region: str) -> list:
    """
    Get all queues for a region.

    Args:
        region: Region code (af, eu, as, us)

    Returns:
        List of queue names for the region
    """
    config = REGION_CONFIG.get(region)
    if not config:
        raise ValueError(f"Unknown region: {region}")
    return config["queues"]


def get_region_for_user(user_id: str, fallback: str = "eu") -> str:
    """
    Determine region for a user (simplified implementation).

    Args:
        user_id: User UUID as string
        fallback: Fallback region if cannot determine

    Returns:
        Region code
    """
    # In production, this would look up user's location from profile
    # or infer from request metadata (IP country, timezone, etc.)
    # For now, return fallback
    return fallback