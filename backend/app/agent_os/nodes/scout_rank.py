"""
Scout Rank Node for Agent OS v2.

Rank and analyze discovered influencers using AI analysis.
"""

import time
import json
from typing import Dict, Any, List
from ...agent_os.runtime import run_async_safe
from ...agent_os.tracer import WarTracer
from ...agent_os.budget import check_budget, add_cost


async def scout_rank(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute scout ranking node.

    Args:
        context: Execution context

    Returns:
        Ranking result with analyzed influencers
    """
    tracer = WarTracer()
    trace_id = context["trace_id"]
    user_id = context["user_id"]

    tracer.log_step(trace_id, "SCOUT RANK START")

    # Check budget
    check_budget(user_id)

    start_time = time.time()

    try:
        # Get previous step results
        step_results = context.get("step_results", {})
        collect_result = step_results.get("scout_collect", {})

        if not collect_result or collect_result.get("status") != "success":
            raise Exception("Scout collect step failed or missing")

        influencers = collect_result.get("influencers", [])
        niche = collect_result.get("niche", "general")

        # Rank influencers
        ranked_influencers = await _rank_influencers(influencers, niche)

        # Generate analysis report
        report = await _generate_analysis_report(ranked_influencers, niche)

        # Add cost
        duration_ms = (time.time() - start_time) * 1000
        cost = max(0.003, len(influencers) * 0.0002)  # Base + per influencer
        add_cost(user_id, cost)

        result = {
            "ranked_influencers": ranked_influencers,
            "report": report,
            "top_3": ranked_influencers[:3],
            "count": len(ranked_influencers),
            "niche": niche,
            "cost": cost,
            "duration_ms": duration_ms,
            "status": "success"
        }

        tracer.log_step(trace_id, f"SCOUT RANK DONE: ranked {len(influencers)} influencers")
        return result

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        tracer.log_step(trace_id, f"SCOUT RANK FAILED: {str(e)}")
        return {
            "error": str(e),
            "duration_ms": duration_ms,
            "status": "failed"
        }


async def _rank_influencers(influencers: List[Dict[str, Any]], niche: str) -> List[Dict[str, Any]]:
    """
    Rank influencers by relevance to niche.

    Args:
        influencers: List of influencer profiles
        niche: Target niche

    Returns:
        Ranked list of influencers
    """
    if not influencers:
        return []

    try:
        # Try AI ranking first
        from ...services.agent_zero_service import analyze_influencers

        # Convert to string for analysis
        influencers_str = json.dumps(influencers, indent=2)
        analysis = analyze_influencers(influencers_data=influencers, niche=niche)

        # Parse analysis and apply ranking
        ranked = _parse_ai_ranking(analysis, influencers)
        if ranked:
            return ranked

    except Exception:
        # Fallback to simple ranking
        pass

    # Fallback: rank by followers * engagement
    for influencer in influencers:
        followers = influencer.get("followers", 0)
        engagement = influencer.get("engagement", 1.0)
        influencer["_score"] = followers * engagement

    ranked = sorted(influencers, key=lambda x: x.get("_score", 0), reverse=True)

    # Remove temporary score
    for influencer in ranked:
        if "_score" in influencer:
            del influencer["_score"]

    return ranked


def _parse_ai_ranking(analysis: str, influencers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse AI analysis to extract ranking.

    Args:
        analysis: AI analysis text
        influencers: Original influencer list

    Returns:
        Ranked influencers or empty list if parsing fails
    """
    # Simple parsing - look for @mentions or names
    ranked_handles = []

    # Extract handles from analysis
    lines = analysis.split('\n')
    for line in lines:
        line_lower = line.lower()
        # Look for @mentions
        if '@' in line:
            parts = line.split('@')
            if len(parts) > 1:
                handle = parts[1].split()[0].strip('.,:;')
                if handle:
                    ranked_handles.append(handle)

        # Look for numbers followed by names
        if any(word in line_lower for word in ['1.', '2.', '3.', 'first', 'second', 'third']):
            # Simple extraction
            for influencer in influencers:
                handle = influencer.get("handle", "").lower().replace('@', '')
                name = influencer.get("name", "").lower()
                if handle and handle in line_lower:
                    ranked_handles.append(handle)
                elif name and name in line_lower:
                    ranked_handles.append(influencer.get("handle", ""))

    # Map handles back to influencers
    ranked = []
    seen_ids = set()

    # Add ranked ones first
    for handle in ranked_handles:
        handle_lower = handle.lower().replace('@', '')
        for influencer in influencers:
            inf_handle = influencer.get("handle", "").lower().replace('@', '')
            if inf_handle == handle_lower and influencer.get("id") not in seen_ids:
                ranked.append(influencer)
                seen_ids.add(influencer.get("id"))
                break

    # Add any remaining influencers
    for influencer in influencers:
        if influencer.get("id") not in seen_ids:
            ranked.append(influencer)

    return ranked[:20]  # Limit to top 20


async def _generate_analysis_report(ranked_influencers: List[Dict[str, Any]], niche: str) -> str:
    """
    Generate analysis report.

    Args:
        ranked_influencers: Ranked influencer list
        niche: Target niche

    Returns:
        Analysis report text
    """
    if not ranked_influencers:
        return f"No influencers found for niche: {niche}"

    top_3 = ranked_influencers[:3]
    total_followers = sum(inf.get("followers", 0) for inf in ranked_influencers)
    avg_engagement = sum(inf.get("engagement", 0) for inf in ranked_influencers) / len(ranked_influencers)

    report_lines = [
        f"# Scout Analysis Report - {niche.capitalize()}",
        f"## Summary",
        f"- **Total influencers found:** {len(ranked_influencers)}",
        f"- **Total reach:** {total_followers:,} followers",
        f"- **Average engagement:** {avg_engagement:.2f}%",
        f"",
        f"## Top 3 Recommendations",
    ]

    for i, inf in enumerate(top_3, 1):
        report_lines.extend([
            f"### {i}. {inf.get('name', 'Unknown')}",
            f"- **Handle:** {inf.get('handle', 'N/A')}",
            f"- **Followers:** {inf.get('followers', 0):,}",
            f"- **Engagement:** {inf.get('engagement', 0):.2f}%",
            f"- **Niche alignment:** {inf.get('niche', 'general')}",
            f"- **Platform:** {inf.get('platform', 'unknown')}",
            f"",
        ])

    report_lines.extend([
        f"## Strategic Insights",
        f"1. **Audience Quality:** {'High' if avg_engagement > 5 else 'Medium' if avg_engagement > 3 else 'Low'}",
        f"2. **Market Saturation:** {'Competitive' if len(ranked_influencers) > 15 else 'Moderate' if len(ranked_influencers) > 8 else 'Emerging'}",
        f"3. **ROI Potential:** {'Excellent' if avg_engagement > 6 else 'Good' if avg_engagement > 4 else 'Moderate'}",
        f"",
        f"## Next Steps",
        f"- Engage with top 3 influencers for initial outreach",
        f"- Monitor mid-tier influencers for growth potential",
        f"- Consider micro-influencers for targeted campaigns",
    ])

    return '\n'.join(report_lines)


# Celery task wrapper
def scout_rank_task(context: Dict[str, Any]) -> Dict[str, Any]:
    """Celery task wrapper for scout rank node."""
    return run_async_safe(scout_rank, context)