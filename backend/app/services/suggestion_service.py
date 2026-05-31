"""
Suggestion Engine — generates personalized AI suggestions for each user.
Sends via Telegram with inline approve/reject buttons.
"""
import logging
import json
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from ..models import User, Agent, AgentSuggestion, AgentMemory, Offer
from ..database import SessionLocal

logger = logging.getLogger(__name__)

SUGGESTION_TEMPLATES = {
    "scout": [
        {"title": "Scout {niche} influencers in {location}", "action": "run_scout"},
        {"title": "Find micro-influencers for {niche}", "action": "run_scout"},
    ],
    "mission": [
        {"title": "Claim nearby offer: {offer_title}", "action": "claim_offer"},
        {"title": "Complete pending mission near you", "action": "start_mission"},
    ],
    "content_gen": [
        {"title": "Generate social posts for {niche}", "action": "generate_content"},
        {"title": "Create viral hook for your niche", "action": "generate_content"},
    ],
}


def _build_fallback_suggestions(user: User, db: Session) -> list[dict]:
    """Template-based suggestions when LLM is unavailable."""
    suggestions = []
    niche = (user.niche_preferences or ["general"])[0] if user.niche_preferences else "general"

    agents = db.query(Agent).filter(Agent.user_id == user.id, Agent.is_active == True).first()

    # Nearby offers → mission suggestions
    offers = db.query(Offer).filter(Offer.status == "active").limit(3).all()
    for offer in offers:
        suggestions.append({
            "type": "mission",
            "title": f"Claim: {offer.title}",
            "description": offer.description or f"Bounty: {offer.bounty_value} TND",
            "action_data": {"action": "claim_offer", "offer_id": str(offer.id)},
        })

    # Scout suggestion based on niche
    suggestions.append({
        "type": "scout",
        "title": f"Scout {niche} influencers in Tunis",
        "description": "Find top local influencers matching your niche",
        "action_data": {"action": "run_scout", "niche": niche, "location": "Tunis"},
    })

    # Content gen suggestion
    suggestions.append({
        "type": "content_gen",
        "title": f"Generate 3 viral hooks for {niche}",
        "description": "AI will create hooks optimized for your niche",
        "action_data": {"action": "generate_content", "niche": niche},
    })

    return suggestions


def generate_suggestions_for_user(user_id: str) -> int:
    """Generate suggestions for a single user. Returns count of suggestions created."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return 0

        suggestions_raw = _build_fallback_suggestions(user, db)

        count = 0
        for s in suggestions_raw:
            agent = db.query(Agent).filter(Agent.user_id == user.id, Agent.is_active == True).first()
            suggestion = AgentSuggestion(
                user_id=user.id,
                agent_id=agent.id if agent else None,
                suggestion_type=s["type"],
                title=s["title"],
                description=s.get("description", ""),
                action_data=s.get("action_data", {}),
                status="pending",
            )
            db.add(suggestion)
            count += 1

        db.commit()
        return count
    except Exception as exc:
        db.rollback()
        logger.error(f"Failed to generate suggestions for user {user_id}: {exc}")
        return 0
    finally:
        db.close()


def generate_all_suggestions() -> dict:
    """Batch generate suggestions for all active users. Runs as Celery beat task."""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.onboarded == True).limit(200).all()
        total = 0
        for user in users:
            total += generate_suggestions_for_user(str(user.id))
        logger.info(f"Generated {total} suggestions across {len(users)} users")
        return {"users_processed": len(users), "suggestions_created": total}
    finally:
        db.close()


def record_suggestion_response(suggestion_id: str, approved: bool) -> Optional[dict]:
    """Record user's response to a suggestion. If approved, return action to execute."""
    db = SessionLocal()
    try:
        suggestion = db.query(AgentSuggestion).filter(AgentSuggestion.id == suggestion_id).first()
        if not suggestion or suggestion.status != "pending":
            return None

        now = datetime.now(timezone.utc)
        suggestion.status = "approved" if approved else "rejected"
        suggestion.responded_at = now

        # Store preference in agent_memories
        if suggestion.user_id and suggestion.suggestion_type:
            from ..models import AgentMemory
            preference = AgentMemory(
                user_id=suggestion.user_id,
                agent_id=suggestion.agent_id,
                memory_type="preference",
                content=json.dumps({
                    "suggestion_type": suggestion.suggestion_type,
                    "title": suggestion.title,
                    "approved": approved,
                }),
                metadata_={
                    "suggestion_id": suggestion_id,
                    "approved": approved,
                    "recorded_at": now.isoformat(),
                },
            )
            db.add(preference)

        db.commit()

        if approved:
            return {
                "action_data": suggestion.action_data,
                "suggestion_type": suggestion.suggestion_type,
                "title": suggestion.title,
            }
        return {"status": "rejected"}
    except Exception as exc:
        db.rollback()
        logger.error(f"Failed to record suggestion response {suggestion_id}: {exc}")
        return None
    finally:
        db.close()


def get_pending_suggestions(user_id: str) -> list[dict]:
    """Get all pending suggestions for a user."""
    db = SessionLocal()
    try:
        suggestions = (
            db.query(AgentSuggestion)
            .filter(AgentSuggestion.user_id == user_id, AgentSuggestion.status == "pending")
            .order_by(AgentSuggestion.created_at.desc())
            .limit(10)
            .all()
        )
        return [
            {
                "id": str(s.id),
                "type": s.suggestion_type,
                "title": s.title,
                "description": s.description,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in suggestions
        ]
    finally:
        db.close()