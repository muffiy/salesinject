"""
Agent OS v2 - Distributed, event‑sourced, self‑healing agent cloud.

A production-ready distributed agent system with:
- Domain-isolated worker clusters
- Redpanda as the single event backbone
- Fault-tolerant workflow engine (retry + fallback + partial results)
- Agent market economy based on performance + stake
- Real-time mission replay and telemetry WebSockets
- Multi-region execution (pluggable)
"""

from .war_engine import WarEngine
from .engine_v2 import WorkflowEngineV2
from .tracer import WarTracer
from .event_bus import EventBus, EVENT_TOPICS
from .market import (
    calculate_score, get_best_agent, record_agent_performance,
    add_stake, remove_stake, get_agent_rankings
)
from .router import get_queue_for_node, get_node_domain, get_all_queues
from .missions import (
    get_mission, get_mission_nodes, list_missions,
    register_mission, update_mission
)
from .budget import check_budget, add_cost, get_budget_usage
from .cost_engine import check_mission_cost, get_mission_cost_today
from .concurrency import check_concurrency, increment_active, decrement_active
from .runtime import run_async_safe, execute_node

__version__ = "2.0.0"
__all__ = [
    # Core engine
    "WarEngine",
    "WorkflowEngineV2",
    "WarTracer",
    "EventBus",
    "EVENT_TOPICS",

    # Market economy
    "calculate_score",
    "get_best_agent",
    "record_agent_performance",
    "add_stake",
    "remove_stake",
    "get_agent_rankings",

    # Routing
    "get_queue_for_node",
    "get_node_domain",
    "get_all_queues",

    # Missions
    "get_mission",
    "get_mission_nodes",
    "list_missions",
    "register_mission",
    "update_mission",

    # Budget and cost
    "check_budget",
    "add_cost",
    "get_budget_usage",
    "check_mission_cost",
    "get_mission_cost_today",

    # Concurrency
    "check_concurrency",
    "increment_active",
    "decrement_active",

    # Runtime
    "run_async_safe",
    "execute_node",
]