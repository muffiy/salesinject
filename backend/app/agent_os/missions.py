"""
Mission Registry for Agent OS v2.

Defines workflow compositions for different mission types.
Each mission is a sequence of nodes executed by the workflow engine.
"""

from typing import Dict, List

MISSIONS: Dict[str, Dict[str, List[str]]] = {
    "scout": {
        "description": "Find and rank influencers in a niche/location",
        "nodes": [
            "hermes_plan",       # Strategic planning
            "scout_collect",     # Influencer discovery
            "scout_analyze",     # Initial analysis
            "scout_rank",        # Ranking and scoring
            "map_render",        # Visual map generation
        ]
    },
    "ammo_generation": {
        "description": "Generate marketing content and ad copy",
        "nodes": [
            "hermes_strategy",   # Content strategy
            "paperclip_generate", # Content creation
            "ammo_validator",    # Quality validation
            "content_enhance",   # Enhancement and optimization
        ]
    },
    "bounty_match": {
        "description": "Match brands with influencers and build contracts",
        "nodes": [
            "hermes_negotiation", # Negotiation strategy
            "matchmaker_agent",   # Brand-influencer matching
            "bounty_analyze",     # Deal analysis
            "contract_builder",   # Contract generation
        ]
    },
    "rapid_scout": {
        "description": "Quick scout with minimal analysis",
        "nodes": [
            "scout_collect",     # Influencer discovery
            "scout_rank",        # Basic ranking
            "map_render",        # Map generation
        ]
    },
    "content_audit": {
        "description": "Audit existing content and suggest improvements",
        "nodes": [
            "hermes_plan",       # Audit planning
            "content_enhance",   # Enhancement suggestions
            "ammo_validator",    # Validation
        ]
    },
    "market_analysis": {
        "description": "Analyze market trends and opportunities",
        "nodes": [
            "hermes_strategy",   # Analysis framework
            "scout_analyze",     # Market analysis
            "bounty_analyze",    # Opportunity analysis
        ]
    },
}


def get_mission(mission_type: str) -> Dict[str, List[str]]:
    """
    Get mission definition by type.

    Args:
        mission_type: Type of mission

    Returns:
        Mission definition with description and nodes

    Raises:
        ValueError: If mission type not found
    """
    mission = MISSIONS.get(mission_type)
    if not mission:
        raise ValueError(f"Unknown mission type: {mission_type}")
    return mission


def get_mission_nodes(mission_type: str) -> List[str]:
    """
    Get node sequence for a mission.

    Args:
        mission_type: Type of mission

    Returns:
        List of node names in execution order
    """
    mission = get_mission(mission_type)
    return mission.get("nodes", [])


def get_mission_description(mission_type: str) -> str:
    """
    Get description for a mission.

    Args:
        mission_type: Type of mission

    Returns:
        Mission description
    """
    mission = get_mission(mission_type)
    return mission.get("description", "")


def register_mission(mission_type: str, nodes: List[str], description: str = "") -> None:
    """
    Register a new mission type.

    Args:
        mission_type: Type of mission
        nodes: List of node names in execution order
        description: Mission description

    Raises:
        ValueError: If mission type already exists
    """
    if mission_type in MISSIONS:
        raise ValueError(f"Mission type '{mission_type}' already registered")

    MISSIONS[mission_type] = {
        "description": description,
        "nodes": nodes
    }


def update_mission(mission_type: str, nodes: List[str] = None, description: str = None) -> None:
    """
    Update an existing mission.

    Args:
        mission_type: Type of mission
        nodes: Optional new node sequence
        description: Optional new description

    Raises:
        ValueError: If mission type not found
    """
    if mission_type not in MISSIONS:
        raise ValueError(f"Mission type '{mission_type}' not found")

    mission = MISSIONS[mission_type]
    if nodes is not None:
        mission["nodes"] = nodes
    if description is not None:
        mission["description"] = description


def unregister_mission(mission_type: str) -> None:
    """
    Unregister a mission type.

    Args:
        mission_type: Type of mission

    Raises:
        ValueError: If mission type not found
    """
    if mission_type not in MISSIONS:
        raise ValueError(f"Mission type '{mission_type}' not found")

    del MISSIONS[mission_type]


def list_missions() -> Dict[str, str]:
    """
    List all available missions.

    Returns:
        Dictionary mapping mission types to descriptions
    """
    return {mt: mission["description"] for mt, mission in MISSIONS.items()}


def validate_mission_nodes(mission_type: str) -> bool:
    """
    Validate that all nodes in a mission are registered.

    Args:
        mission_type: Type of mission

    Returns:
        True if all nodes are valid, False otherwise
    """
    from .router import validate_node

    try:
        nodes = get_mission_nodes(mission_type)
        for node in nodes:
            if not validate_node(node):
                return False
        return True
    except ValueError:
        return False


def get_node_dependencies(node_name: str) -> List[str]:
    """
    Get missions that depend on a specific node.

    Args:
        node_name: Name of the node

    Returns:
        List of mission types that use this node
    """
    dependencies = []
    for mission_type, mission in MISSIONS.items():
        if node_name in mission.get("nodes", []):
            dependencies.append(mission_type)
    return dependencies