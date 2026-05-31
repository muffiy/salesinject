"""
Content Endpoints for Agent OS v2.
Contains content-related skills like repurposing competitor hooks.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.services.openrouter_service import call_llm
from app.services.memory_injection import inject_memory_context
import asyncio

router = APIRouter(prefix="/content", tags=["Content"])


@router.post("/repurpose")
async def repurpose_hook(
    competitor_ad_url: str,
    user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Repurpose a competitor's winning ad hook for the user's brand.

    Args:
        competitor_ad_url: URL of the competitor's ad to analyze and repurpose

    Returns:
        Original hook and repurposed hook for user's brand
    """
    # Fetch competitor ad copy (mock implementation - in production would scrape or use Exa)
    # For now, we'll use a placeholder that would be replaced with actual scraping
    competitor_hook = "Example hook: 'Lose weight fast with our tea!'"  # Placeholder

    # Get user's niche preferences for context
    user_niche = user.niche_preferences[0] if user.niche_preferences else "general"

    # Inject memory context
    try:
        context = await inject_memory_context(
            user_id=str(user.id),
            query=f"Rewrite this hook for my brand in niche {user_niche}: {competitor_hook}",
            limit=3
        )

        if context:
            prompt = f"{context}\n\nRewrite this hook for my brand (niche {user_niche}):\n{competitor_hook}\nReturn only the new hook."
        else:
            prompt = f"Rewrite this hook for my brand (niche {user_niche}):\n{competitor_hook}\nReturn only the new hook."

    except Exception:
        # Fallback if memory injection fails
        prompt = f"Rewrite this hook for my brand (niche {user_niche}):\n{competitor_hook}\nReturn only the new hook."

    # Call LLM to generate repurposed hook
    new_hook = call_llm(prompt, model_tier="cheap")

    return {
        "original_hook": competitor_hook,
        "repurposed_hook": new_hook.strip(),
        "user_niche": user_niche
    }


@router.get("/heatmap")
async def territory_heatmap(
    city: str,
    db: Session = Depends(get_db),
):
    """
    Return aggregated data for frontend map heat layer.

    Args:
        city: City to generate heatmap for (e.g., Tunis)

    Returns:
        Array of locations with intensity values for heatmap visualization
    """
    from app.models import Offer, OfferClaim
    from sqlalchemy import func

    # Group offers by location and count claims
    heat_data = db.query(
        Offer.lat, Offer.lon,
        func.count(OfferClaim.id).label("activity")
    ).outerjoin(OfferClaim, Offer.id == OfferClaim.offer_id).filter(
        Offer.city == city, Offer.status == "active"
    ).group_by(Offer.lat, Offer.lon).all()

    # Format response for frontend heatmap consumption
    result = []
    for row in heat_data:
        # Only include locations with some activity
        if row.activity > 0:
            result.append({
                "lat": float(row.lat),
                "lon": float(row.lon),
                "intensity": int(row.activity)
            })

    return {
        "city": city,
        "heatmap_data": result,
        "total_locations": len(result)
    }