"""
Paperclip Tools — @tool-decorated functions for the AI agent pipeline.

Each tool is registered in _TOOL_REGISTRY for introspection.
Tools are called sequentially by the scout mission orchestrator (paperclip_agent.py).
"""
import uuid
import json
import random
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

# ── Tool Registry ──────────────────────────────────────────────────────────────
_TOOL_REGISTRY: Dict[str, callable] = {}


def tool(func):
    """Decorator that registers a function as a tool."""
    func.is_tool = True
    func.tool_name = func.__name__
    func.tool_description = func.__doc__
    _TOOL_REGISTRY[func.__name__] = func
    return func


def get_all_tools() -> Dict[str, callable]:
    return _TOOL_REGISTRY.copy()


# ── Tool Implementations ──────────────────────────────────────────────────────

@tool
def scout_influencers(niche: str, location: str) -> List[Dict[str, Any]]:
    """Find influencers using Exa.ai neural search or mock data."""
    from ..services.exa_service import find_influencers
    return find_influencers(niche, location)


@tool
def analyze_and_rank(influencers_data: List[Dict[str, Any]], niche: str) -> str:
    """Uses OpenRouter LLM to analyze and rank influencers by niche fit."""
    from ..services.openrouter_service import call_llm

    if not influencers_data:
        return f"No influencers found for niche: {niche}"

    # Sort by followers first as baseline
    ranked = sorted(influencers_data, key=lambda x: x.get("followers", 0), reverse=True)[:10]

    prompt = (
        f"You are an expert Influencer Marketing Agent. Analyze these influencer profiles "
        f"in the '{niche}' niche and provide a concise, ranked report of the top 3 best fits "
        f"for a brand campaign. For each, explain WHY they are a good fit.\n\n"
        f"Influencer Data:\n{json.dumps(ranked, indent=2)}"
    )

    return call_llm(prompt)


@tool
def save_scout_report(
    user_id: str,
    influencers: List[Dict[str, Any]],
    niche: str,
    db: Session,
) -> Dict[str, Any]:
    """Persist scout report with map-ready coordinates for DeckGL rendering."""
    from ..models import ScoutReport

    # Generate map_data with Tunis-area coordinates for each influencer
    map_data = []
    for i, inf in enumerate(influencers):
        lat = inf.get("lat", 36.8065 + random.uniform(-0.05, 0.05))
        lon = inf.get("lon", 10.1815 + random.uniform(-0.05, 0.05))
        map_data.append({
            "name": inf.get("name") or inf.get("handle", f"Creator_{i}"),
            "handle": inf.get("handle", ""),
            "followers": inf.get("followers", 0),
            "engagement": inf.get("engagement", 0),
            "niche": niche,
            "coordinates": [lon, lat],
            "type": "influencer",
        })

    report = ScoutReport(
        user_id=user_id,
        target_niche=niche,
        target_location=influencers[0].get("location", "Tunisia") if influencers else "Tunisia",
        map_data=map_data,
        influencer_count=len(influencers),
    )
    db.add(report)
    db.flush()

    return {"record_id": str(report.id), "map_points": len(map_data)}


@tool
def save_scout_results(
    user_id: str,
    task_id: Optional[str],
    influencers: List[Dict[str, Any]],
    report: str,
    ad_copy: str,
    db: Session,
) -> Dict[str, Any]:
    """Store mission results as PaperclipItems (mission_log, pinned_profiles, ad_copy)."""
    from ..models import PaperclipItem

    rows = 0

    # 1. Mission Log
    log_item = PaperclipItem(
        user_id=user_id,
        task_id=task_id,
        item_type="mission_log",
        content={"report": report},
    )
    db.add(log_item)
    rows += 1

    # 2. Pinned Profiles
    for inf in influencers:
        profile_item = PaperclipItem(
            user_id=user_id,
            task_id=task_id,
            item_type="pinned_profile",
            content=inf,
        )
        db.add(profile_item)
        rows += 1

    # 3. Ad Copy Draft
    copy_item = PaperclipItem(
        user_id=user_id,
        task_id=task_id,
        item_type="ad_copy",
        content={"draft": ad_copy},
    )
    db.add(copy_item)
    rows += 1

    db.flush()
    return {"rows_written": rows}


@tool
def generate_ad_idea_tool(user_id: str, prompt: str, db: Session = None) -> Dict[str, Any]:
    """RAG-augmented content generation: fetch context from memories, call LLM, store result."""
    from ..services.openrouter_service import call_llm
    from ..models import PaperclipItem, AgentMemory

    # RAG: Fetch recent context if DB available
    context_snippets = []
    if db:
        memories = (
            db.query(AgentMemory)
            .filter(AgentMemory.user_id == user_id)
            .order_by(AgentMemory.created_at.desc())
            .limit(5)
            .all()
        )
        context_snippets = [m.content for m in memories if m.content]

        recent_copies = (
            db.query(PaperclipItem)
            .filter(PaperclipItem.user_id == user_id, PaperclipItem.item_type == "ad_copy")
            .order_by(PaperclipItem.created_at.desc())
            .limit(3)
            .all()
        )
        for item in recent_copies:
            if isinstance(item.content, dict):
                context_snippets.append(item.content.get("draft", ""))

    context_block = "\n".join(context_snippets) if context_snippets else "No prior context."

    full_prompt = (
        f"Generate creative marketing content based on this request:\n\n"
        f"Request: {prompt}\n\n"
        f"Context from previous work:\n{context_block}\n\n"
        f"Provide:\n1. A viral hook (max 15 words)\n2. A 60-second video script\n"
        f"3. Three caption options with hashtags\n4. Best posting time for Tunisia"
    )

    result = call_llm(full_prompt)

    # Store the result
    if db:
        item = PaperclipItem(
            user_id=user_id,
            item_type="content_idea",
            content={"prompt": prompt, "result": result},
        )
        db.add(item)
        db.flush()

    return {"content": result}


@tool
def notify_telegram(chat_id: int, message: str) -> Dict[str, str]:
    """Send a Telegram notification — fails silently to not break the pipeline."""
    import asyncio
    try:
        from ..services.telegram_service import send_message
        asyncio.run(send_message(chat_id, message))
        return {"status": "sent"}
    except Exception as e:
        print(f"[Telegram Notify] Failed: {e}")
        return {"status": "failed", "error": str(e)}
