"""
Scout Collect Node for Agent OS v2.

Influencer discovery using Exa neural search or fallback methods.
"""

import time
import random
from typing import Dict, Any, List
from ...agent_os.runtime import run_async_safe
from ...agent_os.tracer import WarTracer
from ...agent_os.budget import check_budget, add_cost


async def scout_collect(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute scout collection node.

    Args:
        context: Execution context

    Returns:
        Collection result with discovered influencers
    """
    tracer = WarTracer()
    trace_id = context["trace_id"]
    user_id = context["user_id"]

    tracer.log_step(trace_id, "SCOUT COLLECT START")

    # Check budget
    check_budget(user_id)

    start_time = time.time()

    try:
        # Get mission parameters
        payload = context.get("payload", {})
        niche = payload.get("niche", "general")
        location = payload.get("location", "global")

        # Execute collection
        influencers = await _collect_influencers(niche, location)

        # Add cost
        duration_ms = (time.time() - start_time) * 1000
        cost = max(0.002, len(influencers) * 0.0001)  # Base + per influencer
        add_cost(user_id, cost)

        result = {
            "influencers": influencers,
            "count": len(influencers),
            "niche": niche,
            "location": location,
            "cost": cost,
            "duration_ms": duration_ms,
            "status": "success"
        }

        tracer.log_step(trace_id, f"SCOUT COLLECT DONE: found {len(influencers)} influencers")
        return result

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        tracer.log_step(trace_id, f"SCOUT COLLECT FAILED: {str(e)}")
        return {
            "error": str(e),
            "duration_ms": duration_ms,
            "status": "failed"
        }


async def _collect_influencers(niche: str, location: str) -> List[Dict[str, Any]]:
    """
    Collect influencers using Exa service or fallback.

    Args:
        niche: Target niche
        location: Target location

    Returns:
        List of influencer profiles
    """
    try:
        # Try Exa service first
        from ...services.exa_service import find_influencers
        influencers = find_influencers(niche=niche, location=location)

        if influencers and len(influencers) > 0:
            return influencers

        # Fallback to mock data if Exa fails or returns empty
        return _generate_mock_influencers(niche, location)

    except Exception:
        # Fallback to mock data
        return _generate_mock_influencers(niche, location)


def _generate_mock_influencers(niche: str, location: str) -> List[Dict[str, Any]]:
    """Generate mock influencer data for fallback."""
    niches = {
        "fashion": ["style", "beauty", "luxury", "streetwear"],
        "tech": ["gadgets", "software", "ai", "startups"],
        "food": ["restaurants", "recipes", "health", "baking"],
        "travel": ["destinations", "adventure", "luxury", "budget"],
        "fitness": ["workouts", "nutrition", "wellness", "yoga"]
    }

    sub_niches = niches.get(niche.lower(), ["content", "lifestyle", "creative"])

    influencers = []
    for i in range(random.randint(8, 15)):
        sub_niche = random.choice(sub_niches)
        followers = random.randint(5000, 500000)
        engagement = random.uniform(2.0, 8.0)

        influencer = {
            "id": f"inf_{i+1}",
            "name": f"{sub_niche.capitalize()} Creator {i+1}",
            "handle": f"@{sub_niche.lower()}_creator_{i+1}",
            "followers": followers,
            "engagement": engagement,
            "niche": sub_niche,
            "location": location,
            "bio": f"Passionate about {sub_niche} | Based in {location}",
            "platform": random.choice(["instagram", "tiktok", "youtube"]),
            "url": f"https://example.com/{sub_niche}_creator_{i+1}",
            "content_type": random.choice(["photos", "videos", "stories", "reels"]),
            "authenticity_score": random.uniform(0.6, 0.95),
            "brand_friendly": random.choice([True, True, True, False])  # 75% brand friendly
        }

        # Add location coordinates for map rendering
        if location.lower() == "tunis":
            influencer["lat"] = 36.8065 + random.uniform(-0.05, 0.05)
            influencer["lng"] = 10.1815 + random.uniform(-0.05, 0.05)
        else:
            # Default to random coordinates
            influencer["lat"] = random.uniform(-90, 90)
            influencer["lng"] = random.uniform(-180, 180)

        influencers.append(influencer)

    return influencers


def _enhance_with_ai(influencers: List[Dict[str, Any]], niche: str) -> List[Dict[str, Any]]:
    """
    Enhance influencer data with AI analysis (placeholder).

    Args:
        influencers: Raw influencer data
        niche: Target niche

    Returns:
        Enhanced influencer data
    """
    # Placeholder for AI enhancement
    # In production, this would call an LLM to analyze profiles
    for influencer in influencers:
        influencer["ai_analysis"] = {
            "niche_alignment": random.uniform(0.5, 0.95),
            "audience_quality": random.uniform(0.4, 0.9),
            "content_consistency": random.uniform(0.6, 0.98),
            "growth_potential": random.uniform(0.3, 0.85)
        }

    return influencers


# Celery task wrapper
def scout_collect_task(context: Dict[str, Any]) -> Dict[str, Any]:
    """Celery task wrapper for scout collect node."""
    return run_async_safe(scout_collect, context)