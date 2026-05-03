from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import Session

from ..models import OfferClaim, Offer

MISSION_STATES = ("claimed", "arrived", "submitted", "ai_reviewed", "completed", "paid")


def _must_transition(current: str, expected: str) -> None:
    if current != expected:
        raise ValueError(f"Invalid state transition: expected {expected}, got {current}")


def claim_mission(db: Session, user_id: str, offer_id: str) -> OfferClaim:
    user_uuid = uuid.UUID(user_id)
    offer_uuid = uuid.UUID(offer_id)
    existing = db.query(OfferClaim).filter(
        OfferClaim.offer_id == offer_uuid,
        OfferClaim.influencer_id == user_uuid,
    ).first()
    if existing:
        return existing

    offer = db.query(Offer).filter(Offer.id == offer_uuid, Offer.status == "active").first()
    if not offer:
        raise ValueError("Offer not active")

    claim = OfferClaim(
        offer_id=offer_uuid,
        influencer_id=user_uuid,
        status="claimed",
        payout_amount=float(offer.bounty_value or 0),
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def start_mission(db: Session, claim_id: str) -> OfferClaim:
    claim = db.query(OfferClaim).filter(OfferClaim.id == uuid.UUID(claim_id)).first()
    if not claim:
        raise ValueError("Claim not found")
    _must_transition(claim.status, "claimed")
    claim.status = "arrived"
    db.commit()
    db.refresh(claim)
    return claim


def check_geofence(db: Session, claim_id: str, lat: float, lon: float) -> bool:
    _ = (lat, lon)
    claim = db.query(OfferClaim).filter(OfferClaim.id == uuid.UUID(claim_id)).first()
    if not claim:
        return False
    if claim.status in ("arrived", "submitted", "ai_reviewed", "completed", "paid"):
        return True
    _must_transition(claim.status, "claimed")
    claim.status = "arrived"
    db.commit()
    return True


def submit_mission(db: Session, claim_id: str) -> OfferClaim:
    claim = db.query(OfferClaim).filter(OfferClaim.id == uuid.UUID(claim_id)).first()
    if not claim:
        raise ValueError("Claim not found")
    _must_transition(claim.status, "arrived")
    claim.status = "submitted"
    db.commit()
    db.refresh(claim)
    return claim


def mark_ai_reviewed(db: Session, claim_id: str) -> None:
    claim = db.query(OfferClaim).filter(OfferClaim.id == uuid.UUID(claim_id)).first()
    if not claim:
        raise ValueError("Claim not found")
    _must_transition(claim.status, "submitted")
    claim.status = "ai_reviewed"
    db.commit()



def boost_mission(db: Session, claim_id: str) -> OfferClaim:
    claim = db.query(OfferClaim).filter(OfferClaim.id == uuid.UUID(claim_id)).first()
    if not claim:
        raise ValueError("Claim not found")
    if claim.status in ("completed", "paid"):
        return claim
    claim.boosted = True
    claim.payout_amount = round(float(claim.payout_amount or 0) * 1.3, 2)
    db.commit()
    db.refresh(claim)
    return claim

def resolve_competition(db: Session, claim_id: str) -> dict:
    claim_uuid = uuid.UUID(claim_id)
    claim = db.query(OfferClaim).filter(OfferClaim.id == claim_uuid).with_for_update().first()
    if not claim:
        return {"winner": False, "position": 99}
    all_completed = (
        db.query(OfferClaim)
        .filter(OfferClaim.offer_id == claim.offer_id, OfferClaim.completed_at.isnot(None))
        .order_by(OfferClaim.completed_at.asc())
        .all()
    )
    for idx, c in enumerate(all_completed):
        if c.id == claim_uuid:
            return {"winner": idx == 0, "position": idx + 1}
    return {"winner": False, "position": len(all_completed) + 1}


def finalize_mission(db: Session, claim_id: str, payout: float, position: int) -> None:
    claim = db.query(OfferClaim).filter(OfferClaim.id == uuid.UUID(claim_id)).first()
    if not claim or claim.status == "completed":
        return
    _must_transition(claim.status, "ai_reviewed")
    claim.status = "completed"
    claim.completed_at = datetime.now(timezone.utc)
    claim.payout_amount = payout
    claim.position = position
    db.commit()
