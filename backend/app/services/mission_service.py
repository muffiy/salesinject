from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..models import OfferClaim

MISSION_STATES = ("created", "claimed", "in_progress", "arrived", "submitted", "completed")


def _must_transition(current: str, expected: str) -> None:
    if current != expected:
        raise ValueError(f"Invalid state transition: expected {expected}, got {current}")


def claim_mission(db: Session, user_id: str, offer_id: str) -> OfferClaim:
    claim = OfferClaim(offer_id=uuid.UUID(offer_id), influencer_id=uuid.UUID(user_id), status="claimed")
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def start_mission(db: Session, claim_id: str) -> None:
    claim = db.query(OfferClaim).filter(OfferClaim.id == uuid.UUID(claim_id)).first()
    if not claim:
        raise ValueError("Claim not found")
    _must_transition(claim.status, "claimed")
    claim.status = "in_progress"
    db.commit()


def check_geofence(db: Session, claim_id: str, lat: float, lon: float) -> bool:
    _ = (lat, lon)
    claim = db.query(OfferClaim).filter(OfferClaim.id == uuid.UUID(claim_id)).first()
    if not claim:
        return False
    if claim.status == "arrived":
        return True
    _must_transition(claim.status, "in_progress")
    claim.status = "arrived"
    db.commit()
    return True


def mark_submitted(db: Session, claim_id: str) -> None:
    claim = db.query(OfferClaim).filter(OfferClaim.id == uuid.UUID(claim_id)).first()
    if not claim:
        raise ValueError("Claim not found")
    _must_transition(claim.status, "arrived")
    claim.status = "submitted"
    db.commit()


def resolve_competition(db: Session, claim_id: str) -> dict:
    claim_uuid = uuid.UUID(claim_id)
    claim = db.query(OfferClaim).filter(OfferClaim.id == claim_uuid).with_for_update().first()
    if not claim:
        return {"winner": False, "position": 99}
    all_claims = (
        db.query(OfferClaim)
        .filter(OfferClaim.offer_id == claim.offer_id, OfferClaim.completed_at.isnot(None))
        .order_by(OfferClaim.completed_at.asc())
        .all()
    )
    for idx, c in enumerate(all_claims):
        if c.id == claim_uuid:
            return {"winner": idx == 0, "position": idx + 1}
    return {"winner": False, "position": len(all_claims) + 1}


def finalize_mission(db: Session, claim_id: str, payout: float, position: int) -> None:
    claim = db.query(OfferClaim).filter(OfferClaim.id == uuid.UUID(claim_id)).first()
    if not claim:
        return
    if claim.status == "completed":
        return
    _must_transition(claim.status, "submitted")
    claim.status = "completed"
    claim.completed_at = datetime.now(timezone.utc)
    claim.payout_amount = payout
    claim.position = position
    db.commit()
