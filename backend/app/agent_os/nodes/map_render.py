"""
Map Render Node for Agent OS v2.

Generates map data for visualization of scout mission results.
"""

import time
import json
from typing import Dict, Any, List
from ...agent_os.runtime import run_async_safe
from ...agent_os.tracer import WarTracer
from ...agent_os.budget import check_budget, add_cost
from ...agent_os.event_bus import emit_mission_progress


async def map_render(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute map rendering node.

    Args:
        context: Execution context

    Returns:
        Map data for visualization
    """
    tracer = WarTracer()
    trace_id = context["trace_id"]
    user_id = context["user_id"]

    tracer.log_step(trace_id, "MAP RENDER START")

    # Check budget
    check_budget(user_id)

    start_time = time.time()

    try:
        # Get previous step results
        step_results = context.get("step_results", {})
        collect_result = step_results.get("scout_collect", {})
        rank_result = step_results.get("scout_rank", {})

        # Prefer ranked influencers, fallback to collected
        if rank_result and rank_result.get("status") == "success":
            influencers = rank_result.get("ranked_influencers", [])
        elif collect_result and collect_result.get("status") == "success":
            influencers = collect_result.get("influencers", [])
        else:
            raise Exception("No influencer data available for map rendering")

        # Generate map data
        map_data = await _generate_map_data(influencers, context)

        # Add cost
        duration_ms = (time.time() - start_time) * 1000
        cost = 0.001  # Fixed low cost for map rendering
        add_cost(user_id, cost)

        # Emit map update event
        emit_mission_progress(
            trace_id,
            "map_render",
            "completed",
            {"points": len(map_data), "duration_ms": duration_ms}
        )

        result = {
            "map_data": map_data,
            "point_count": len(map_data),
            "bounds": _calculate_map_bounds(map_data),
            "clusters": _cluster_points(map_data),
            "cost": cost,
            "duration_ms": duration_ms,
            "status": "success"
        }

        tracer.log_step(trace_id, f"MAP RENDER DONE: {len(map_data)} points")
        return result

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        tracer.log_step(trace_id, f"MAP RENDER FAILED: {str(e)}")
        return {
            "error": str(e),
            "duration_ms": duration_ms,
            "status": "failed"
        }


async def _generate_map_data(influencers: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate map data from influencer profiles.

    Args:
        influencers: Influencer profiles
        context: Execution context

    Returns:
        Map points for visualization
    """
    mission_type = context.get("mission_type", "scout")
    payload = context.get("payload", {})
    niche = payload.get("niche", "general")

    map_points = []

    for i, influencer in enumerate(influencers):
        # Extract or generate coordinates
        lat = influencer.get("lat")
        lng = influencer.get("lng")

        # Generate coordinates if not present
        if lat is None or lng is None:
            # Generate Tunis-centered coordinates for demo
            lat = 36.8065 + (i * 0.01) - 0.05
            lng = 10.1815 + (i * 0.01) - 0.05

        # Determine point type based on influencer data
        point_type = "influencer"
        if influencer.get("followers", 0) > 100000:
            point_type = "influencer_large"
        elif influencer.get("followers", 0) < 10000:
            point_type = "influencer_small"

        # Calculate score for color coding
        followers = influencer.get("followers", 0)
        engagement = influencer.get("engagement", 0)
        score = min(100, int((followers / 1000) * (engagement / 10)))

        map_point = {
            "id": f"point_{i}",
            "type": point_type,
            "coordinates": [lng, lat],  # GeoJSON format: [lng, lat]
            "properties": {
                "name": influencer.get("name", f"Influencer {i+1}"),
                "handle": influencer.get("handle", ""),
                "followers": followers,
                "engagement": engagement,
                "niche": influencer.get("niche", niche),
                "platform": influencer.get("platform", "unknown"),
                "score": score,
                "rank": i + 1,
                "url": influencer.get("url", ""),
                "content_type": influencer.get("content_type", "mixed")
            },
            "metadata": {
                "mission_type": mission_type,
                "niche": niche,
                "timestamp": time.time()
            }
        }

        map_points.append(map_point)

    return map_points


def _calculate_map_bounds(map_points: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate map bounds from points.

    Args:
        map_points: List of map points

    Returns:
        Bounds dictionary
    """
    if not map_points:
        return {
            "north": 36.9,
            "south": 36.7,
            "east": 10.3,
            "west": 10.0,
            "center_lat": 36.8,
            "center_lng": 10.15
        }

    lats = [point["coordinates"][1] for point in map_points]
    lngs = [point["coordinates"][0] for point in map_points]

    return {
        "north": max(lats) + 0.01,
        "south": min(lats) - 0.01,
        "east": max(lngs) + 0.01,
        "west": min(lngs) - 0.01,
        "center_lat": sum(lats) / len(lats),
        "center_lng": sum(lngs) / len(lngs)
    }


def _cluster_points(map_points: List[Dict[str, Any]], max_distance: float = 0.02) -> List[Dict[str, Any]]:
    """
    Cluster nearby map points.

    Args:
        map_points: List of map points
        max_distance: Maximum distance for clustering (degrees)

    Returns:
        List of clusters
    """
    if len(map_points) <= 5:
        return []

    clusters = []
    visited = set()

    for i, point in enumerate(map_points):
        if i in visited:
            continue

        cluster_points = [point]
        visited.add(i)

        for j, other_point in enumerate(map_points[i+1:], i+1):
            if j in visited:
                continue

            # Calculate distance (simplified)
            lat1, lng1 = point["coordinates"][1], point["coordinates"][0]
            lat2, lng2 = other_point["coordinates"][1], other_point["coordinates"][0]

            distance = abs(lat1 - lat2) + abs(lng1 - lng2)

            if distance < max_distance:
                cluster_points.append(other_point)
                visited.add(j)

        if len(cluster_points) > 1:
            # Calculate cluster center
            lats = [p["coordinates"][1] for p in cluster_points]
            lngs = [p["coordinates"][0] for p in cluster_points]

            cluster = {
                "id": f"cluster_{len(clusters)}",
                "type": "cluster",
                "coordinates": [sum(lngs) / len(lngs), sum(lats) / len(lats)],
                "properties": {
                    "point_count": len(cluster_points),
                    "avg_followers": sum(p["properties"]["followers"] for p in cluster_points) / len(cluster_points),
                    "avg_engagement": sum(p["properties"]["engagement"] for p in cluster_points) / len(cluster_points),
                    "niches": list(set(p["properties"]["niche"] for p in cluster_points))
                }
            }

            clusters.append(cluster)

    return clusters


# Celery task wrapper
def map_render_task(context: Dict[str, Any]) -> Dict[str, Any]:
    """Celery task wrapper for map render node."""
    return run_async_safe(map_render, context)