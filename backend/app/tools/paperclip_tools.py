"""
Paperclip Tool-Use Layer — Scout Mission Pipeline

These @tool-decorated functions are the callable building blocks
that a future LLM agent orchestrator (Agent Zero, LangChain, etc.)
can invoke by name. Each tool is independently executable and
maps cleanly to one service in the backend.

Tool call flow:
    scout_influencers() → analyze_and_rank() → save_scout_results()
"""

from functools import wraps
from typing import Any, Callable, List, Dict


# ---------------------------------------------------------------------------
# Minimal @tool decorator
# Stores tool metadata on the function for future orchestrator discovery.
# Compatible with a future swap to LangChain's @tool or Agent Zero's registry.
# ---------------------------------------------------------------------------

_TOOL_REGISTRY: Dict[str, Callable] = {}


def tool(func: Callable) -> Callable:
    """
    Lightweight @tool decorator.
    Registers the function in the global tool registry and
    exposes its name and docstring as metadata attributes.
    """
    func.is_tool = True  # type: ignore[attr-defined]
    func.tool_name = func.__name__  # type: ignore[attr-defined]
    func.tool_description = (func.__doc__ or "").strip()  # type: ignore[attr-defined]
    _TOOL_REGISTRY[func.__name__] = func

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def get_tool(name: str) -> Callable:
    """Look up a registered tool by name. Useful for dynamic orchestration."""
    if name not in _TOOL_REGISTRY:
        raise KeyError(f"Tool '{name}' is not registered. Available: {list(_TOOL_REGISTRY)}")
    return _TOOL_REGISTRY[name]


# ---------------------------------------------------------------------------
# Tool 1: Scout Influencers
# ---------------------------------------------------------------------------

@tool
def scout_influencers(niche: str, location: str) -> List[Dict]:
    """
    Search for high-value influencers in a given niche and location.

    Calls exa_service.find_influencers() which hits the Exa Neural Search API
    and returns a structured list. Falls back to mock data gracefully if the
    API key is not configured.

    Args:
        niche:    Target content category (e.g. "Fashion", "SaaS", "Food").
        location: Geographic scope (e.g. "Tunisia", "MENA", "Cairo").

    Returns:
        List of influencer dicts:
        [{ name, handle, followers, engagement, location }, ...]
    """
    from ..services.exa_service import find_influencers
    return find_influencers(niche=niche, location=location)


# ---------------------------------------------------------------------------
# Tool 2: Analyze and Rank
# ---------------------------------------------------------------------------

@tool
def analyze_and_rank(influencers_data: List[Dict], niche: str) -> str:
    """
    Run Agent Zero analysis on a list of influencer profiles.

    Produces a ranked plain-text report of the top 3 targets,
    sorted by follower count. The stub is deterministic; swap
    the underlying function with an LLM call when ready.

    Args:
        influencers_data: Output from scout_influencers().
        niche:            The niche context for report framing.

    Returns:
        A formatted multi-line ranking report string.
    """
    from ..services.agent_zero_service import analyze_influencers
    return analyze_influencers(influencers_data=influencers_data, niche=niche)


# ---------------------------------------------------------------------------
# Tool 3: Save Scout Results
# ---------------------------------------------------------------------------

@tool
def save_scout_results(
    user_id: str,
    task_id: str,
    influencers: List[Dict],
    report: str,
    ad_copy: str,
    db: Any,
) -> Dict:
    """
    Persist a completed scout mission to the Paperclip database layer.

    Writes 3 types of rows into `paperclip_items`:
    - 1 × mission_log   (the full Agent Zero report string)
    - N × pinned_profile (one row per influencer found)
    - 1 × ad_copy        (an initial draft string for brand outreach)

    The `db` session is passed in from the Celery task to ensure
    all writes share the same SQLAlchemy transaction context.

    Args:
        user_id:     UUID string of the requesting user.
        task_id:     UUID string of the parent Celery task (or None).
        influencers: List of influencer dict from scout_influencers().
        report:      Ranked report string from analyze_and_rank().
        ad_copy:     Draft ad copy string (may be pre-generated or a stub).
        db:          Active SQLAlchemy Session from the caller.

    Returns:
        {"status": "ok", "rows_written": N}
    """
    from ..services.paperclip_service import write_paperclip_items

    write_paperclip_items(
        db=db,
        user_id=user_id,
        task_id=task_id,
        influencers=influencers,
        report=report,
        ad_copy=ad_copy,
    )

    # 1 mission_log + len(influencers) pinned_profiles + 1 ad_copy
    rows_written = 1 + len(influencers) + 1
    return {"status": "ok", "rows_written": rows_written}


# ---------------------------------------------------------------------------
# Tool 4: Save Scout Report
# ---------------------------------------------------------------------------

@tool
def save_scout_report(user_id: str, influencers: List[Dict], niche: str, db: Any) -> Dict:
    """
    Write a structured scout result into the `scout_reports` table.

    Converts the influencer list produced by scout_influencers() into
    the map_data JSONB format expected by ScoutReport, then flushes
    within the caller's transaction (caller is responsible for commit).

    Args:
        user_id:     UUID string of the requesting user.
        influencers: Structured list from scout_influencers().
        niche:       Niche string stored on the report row.
        db:          Active SQLAlchemy Session shared from Celery task.

    Returns:
        {"status": "ok", "record_id": str}
    """
    from ..models import ScoutReport
    import uuid

    # Map influencer dicts to the map_data schema used by the frontend DeckGLMap
    map_data = [
        {
            "id": f"inf_{i}",
            "name": inf.get("name", f"Operative_{i}"),
            "handle": inf.get("handle", ""),
            "lat": inf.get("lat", 36.8065 + (i * 0.05)),   # fallback scatter near Tunis
            "lng": inf.get("lng", 10.1815 + (i * 0.05)),
            "followers": inf.get("followers", 0),
            "engagement_rate": inf.get("engagement", 0.0),
            "niche": niche,
        }
        for i, inf in enumerate(influencers)
    ]

    record_id = uuid.uuid4()
    report = ScoutReport(
        id=record_id,
        user_id=user_id,
        target_niche=niche,
        map_data=map_data,
    )
    db.add(report)
    db.flush()  # caller commits
    return {"status": "ok", "record_id": str(record_id)}


# ---------------------------------------------------------------------------
# Tool 5: Notify Telegram
# ---------------------------------------------------------------------------

@tool
def notify_telegram(chat_id: int, message: str) -> Dict:
    """
    Send a Telegram message to a specific chat_id.

    Wraps the async telegram_service.send_message() in asyncio.run()
    so it can be called synchronously from a Celery worker without
    requiring an event loop to already be running.

    Fails silently — a notification error must never crash a Celery task.

    Args:
        chat_id: Telegram chat ID of the target user.
        message: Plain-text message string to send.

    Returns:
        {"status": "sent"} on success, {"status": "failed", "error": ...} on failure.
    """
    import asyncio
    from ..services.telegram_service import send_message

    try:
        asyncio.run(send_message(chat_id=chat_id, text=message))
        return {"status": "sent"}
    except Exception as exc:
        # Log but never propagate — Telegram outage must not fail the mission
        print(f"[notify_telegram] Failed to notify chat_id={chat_id}: {exc}")
        return {"status": "failed", "error": str(exc)}
