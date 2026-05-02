"""
Hermes Plan Node for Agent OS v2.

Strategic planning node for mission initialization and strategy formulation.
"""

import time
from typing import Dict, Any
from ...agent_os.runtime import run_async_safe
from ...agent_os.tracer import WarTracer
from ...agent_os.budget import check_budget, add_cost


async def hermes_plan(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute Hermes planning node.

    Args:
        context: Execution context with user_id, session_id, trace_id, payload

    Returns:
        Planning result
    """
    tracer = WarTracer()
    trace_id = context["trace_id"]
    user_id = context["user_id"]

    tracer.log_step(trace_id, "HERMES PLAN START")

    # Check budget
    check_budget(user_id)

    start_time = time.time()

    try:
        # Extract mission parameters
        payload = context.get("payload", {})
        mission_type = context.get("mission_type", "unknown")

        # Generate strategic plan based on mission type
        if mission_type == "scout":
            plan = await _plan_scout_mission(payload)
        elif mission_type == "ammo_generation":
            plan = await _plan_ammo_generation(payload)
        elif mission_type == "bounty_match":
            plan = await _plan_bounty_match(payload)
        else:
            plan = await _plan_generic(payload, mission_type)

        # Add cost
        duration_ms = (time.time() - start_time) * 1000
        cost = max(0.001, duration_ms / 10000)  # $0.001 per 10 seconds
        add_cost(user_id, cost)

        result = {
            "plan": plan,
            "cost": cost,
            "duration_ms": duration_ms,
            "status": "success"
        }

        tracer.log_step(trace_id, "HERMES PLAN DONE")
        return result

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        tracer.log_step(trace_id, f"HERMES PLAN FAILED: {str(e)}")
        return {
            "error": str(e),
            "duration_ms": duration_ms,
            "status": "failed"
        }


async def _plan_scout_mission(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Plan a scout mission."""
    niche = payload.get("niche", "general")
    location = payload.get("location", "global")

    return {
        "mission_type": "scout",
        "strategy": "neural_search_rank",
        "parameters": {
            "niche": niche,
            "location": location,
            "depth": "comprehensive",
            "focus": ["relevance", "engagement", "authenticity"],
            "estimated_targets": 20
        },
        "timeline": {
            "search_phase": "0-30s",
            "analysis_phase": "30-90s",
            "ranking_phase": "90-120s",
            "reporting_phase": "120-150s"
        },
        "success_criteria": {
            "min_targets": 5,
            "max_duration_s": 180,
            "quality_threshold": 0.7
        }
    }


async def _plan_ammo_generation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Plan ammo (content) generation mission."""
    prompt = payload.get("prompt", "")
    style = payload.get("style", "professional")

    return {
        "mission_type": "ammo_generation",
        "strategy": "rag_enhanced_generation",
        "parameters": {
            "prompt": prompt,
            "style": style,
            "variants": 3,
            "length": "medium",
            "tone": "engaging",
            "hashtags": True
        },
        "timeline": {
            "research_phase": "0-15s",
            "draft_phase": "15-45s",
            "refinement_phase": "45-75s",
            "validation_phase": "75-90s"
        },
        "success_criteria": {
            "readability_score": 0.8,
            "engagement_potential": 0.7,
            "brand_alignment": 0.6
        }
    }


async def _plan_bounty_match(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Plan bounty matching mission."""
    brand_profile = payload.get("brand_profile", {})
    influencer_criteria = payload.get("influencer_criteria", {})

    return {
        "mission_type": "bounty_match",
        "strategy": "multi_factor_matching",
        "parameters": {
            "brand_profile": brand_profile,
            "influencer_criteria": influencer_criteria,
            "matching_factors": ["niche", "audience", "style", "values"],
            "max_candidates": 10
        },
        "timeline": {
            "profile_analysis": "0-20s",
            "candidate_search": "20-60s",
            "matching_scoring": "60-90s",
            "recommendation_gen": "90-120s"
        },
        "success_criteria": {
            "match_score_threshold": 0.75,
            "diversity_score": 0.6,
            "roi_potential": 0.65
        }
    }


async def _plan_generic(payload: Dict[str, Any], mission_type: str) -> Dict[str, Any]:
    """Plan generic mission."""
    return {
        "mission_type": mission_type,
        "strategy": "standard_execution",
        "parameters": payload,
        "timeline": {
            "phase_1": "0-30s",
            "phase_2": "30-60s",
            "phase_3": "60-90s"
        },
        "success_criteria": {
            "completion": True,
            "quality": 0.5
        }
    }


# Celery task wrapper
def hermes_plan_task(context: Dict[str, Any]) -> Dict[str, Any]:
    """Celery task wrapper for Hermes plan node."""
    return run_async_safe(hermes_plan, context)