"""
Offers API — location-based brand offers that influencers claim and complete.
"""
import uuid
import secrets
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Any

from ...deps import get_db, get_current_user, get_current_brand
from ....models import User, Offer, OfferClaim, OfferPerformance
from ....tasks import send_offer_alerts, process_payout
from ....services.mission_service import mark_submitted

router = APIRouter()


# ── Schemas ────────────────────────────────────────────────────────────────────

class OfferCreate(BaseModel):
    title: str
    description: str = ""
    lat: float
    lon: float
    discount_value: float = 0.0
    bounty_value: float = 0.0
    max_claims: int = 50
    expires_in_hours: Optional[int] = None  # None = no expiry


class OfferOut(BaseModel):
    id: str
    title: str
    description: str
    lat: float
    lon: float
    discount_value: float
    bounty_value: float
    status: str
    current_claims: int
    max_claims: int
    promo_code: Optional[str]
    expires_at: Optional[str]
    created_at: str

    model_config = {"from_attributes": True}


class ClaimOut(BaseModel):
    id: str
    offer_id: str
    status: str
    unique_code: str
    created_at: str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/", response_model=OfferOut, status_code=201)
def create_offer(
    payload: OfferCreate,
    current_user: User = Depends(get_current_brand),
    db: Session = Depends(get_db),
):
    """Brand creates a new location-based offer."""
    from datetime import timedelta

    expires_at = None
    if payload.expires_in_hours:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=payload.expires_in_hours)

    promo_code = f"SI-{secrets.token_hex(4).upper()}"

    db_offer = Offer(
        brand_id=current_user.id,
        title=payload.title,
        description=payload.description,
        lat=payload.lat,
        lon=payload.lon,
        discount_value=payload.discount_value,
        bounty_value=payload.bounty_value,
        promo_code=promo_code,
        max_claims=payload.max_claims,
        expires_at=expires_at,
    )
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)

    # Fire async notification to nearby creators
    send_offer_alerts.delay(str(db_offer.id))

    return _offer_to_out(db_offer)


@router.get("/nearby", response_model=List[OfferOut])
def get_nearby_offers(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(10.0, description="Search radius in km"),
    db: Session = Depends(get_db),
):
    """Return active offers near a location. Uses basic bounding box (PostGIS upgrade later)."""
    # ~0.009 degrees ≈ 1km at Tunisia's latitude
    delta = radius_km * 0.009
    offers = (
        db.query(Offer)
        .filter(
            Offer.status == "active",
            Offer.lat.between(lat - delta, lat + delta),
            Offer.lon.between(lon - delta, lon + delta),
        )
        .order_by(Offer.created_at.desc())
        .limit(50)
        .all()
    )
    return [_offer_to_out(o) for o in offers]


@router.get("/", response_model=List[OfferOut])
def list_all_offers(
    status: str = Query("active"),
    db: Session = Depends(get_db),
):
    """List all offers by status."""
    offers = (
        db.query(Offer)
        .filter(Offer.status == status)
        .order_by(Offer.created_at.desc())
        .limit(100)
        .all()
    )
    return [_offer_to_out(o) for o in offers]


@router.post("/{offer_id}/claim", response_model=ClaimOut)
def claim_offer(
    offer_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Influencer claims an offer — generates a unique tracking code."""
    try:
        oid = uuid.UUID(offer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid offer_id format")

    offer = db.query(Offer).filter(Offer.id == oid, Offer.status == "active").first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found or no longer active")

    if offer.current_claims >= offer.max_claims:
        raise HTTPException(status_code=409, detail="Offer is fully claimed")

    # Prevent double-claiming
    existing = db.query(OfferClaim).filter(
        OfferClaim.offer_id == oid,
        OfferClaim.influencer_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You already claimed this offer")

    unique_code = f"{offer.promo_code}-{secrets.token_hex(3).upper()}"

    claim = OfferClaim(
        offer_id=oid,
        influencer_id=current_user.id,
        unique_code=unique_code,
    )
    db.add(claim)
    offer.current_claims += 1
    db.commit()
    db.refresh(claim)

    return ClaimOut(
        id=str(claim.id),
        offer_id=str(claim.offer_id),
        status=claim.status,
        unique_code=claim.unique_code,
        created_at=claim.created_at.isoformat() if claim.created_at else "",
    )


@router.post("/{offer_id}/complete")
def complete_offer(
    offer_id: str,
    proof_url: str = Query(..., description="URL of proof content (video/image)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload proof and trigger review — marks claim as pending_review."""
    try:
        offer_uuid = uuid.UUID(offer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid offer_id format")

    claim = (
        db.query(OfferClaim)
        .filter(
            OfferClaim.offer_id == offer_uuid,
            OfferClaim.influencer_id == current_user.id,
            OfferClaim.status.in_(["claimed", "in_progress", "arrived", "submitted"]),
        )
        .first()
    )
    if not claim:
        raise HTTPException(status_code=404, detail="No active claim found for this offer")

    if claim.status == "submitted":
        return {"message": "Proof already submitted", "claim_id": str(claim.id)}

    if claim.status != "arrived":
        raise HTTPException(status_code=400, detail="Must arrive before submitting")

    try:
        mark_submitted(db, str(claim.id))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    claim.proof_url = proof_url
    db.commit()

    return {"message": "Proof submitted — under review", "claim_id": str(claim.id)}


@router.post("/{offer_id}/approve/{claim_id}")
def approve_claim(
    offer_id: str,
    claim_id: str,
    current_user: User = Depends(get_current_brand),
    db: Session = Depends(get_db),
):
    """Brand approves a claim — triggers payout processing."""
    claim = db.query(OfferClaim).filter(OfferClaim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    offer = db.query(Offer).filter(Offer.id == claim.offer_id).first()
    if not offer or str(offer.brand_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Only the offer creator can approve")

    claim.status = "completed"
    claim.completed_at = datetime.now(timezone.utc)
    db.commit()

    # Trigger async payout
    process_payout.delay(str(claim.id))

    return {"message": "Claim approved — payout processing", "claim_id": str(claim.id)}


@router.post("/webhooks/sale")
def webhook_sale(
    promo_code: str,
    sale_amount: float,
    db: Session = Depends(get_db),
):
    """External webhook from brand's POS/Shopify — track conversions."""
    claim = db.query(OfferClaim).filter(OfferClaim.unique_code == promo_code).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Promo code not found")

    perf = db.query(OfferPerformance).filter(OfferPerformance.claim_id == claim.id).first()
    if not perf:
        perf = OfferPerformance(claim_id=claim.id)
        db.add(perf)

    perf.conversions += 1
    perf.generated_revenue = float(perf.generated_revenue or 0) + sale_amount
    db.commit()

    return {"status": "tracked", "conversions": perf.conversions, "total_revenue": float(perf.generated_revenue)}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _offer_to_out(o: Offer) -> OfferOut:
    return OfferOut(
        id=str(o.id),
        title=o.title or "",
        description=o.description or "",
        lat=float(o.lat),
        lon=float(o.lon),
        discount_value=float(o.discount_value or 0),
        bounty_value=float(o.bounty_value or 0),
        status=o.status or "active",
        current_claims=o.current_claims or 0,
        max_claims=o.max_claims or 50,
        promo_code=o.promo_code,
        expires_at=o.expires_at.isoformat() if o.expires_at else None,
        created_at=o.created_at.isoformat() if o.created_at else "",
    )


@router.post("/{offer_id}/boost")
def boost_offer_reward(offer_id: str, db: Session = Depends(get_db)):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    now = datetime.now(timezone.utc)
    if int(offer.boost_count or 0) >= 3:
        raise HTTPException(status_code=400, detail="Max boosts reached")
    if offer.last_boosted_at and (now - offer.last_boosted_at) < timedelta(seconds=60):
        raise HTTPException(status_code=429, detail="Boost cooldown active")

    offer.bounty_value = round(float(offer.bounty_value or 0) * 1.2, 2)
    offer.boost_count = int(offer.boost_count or 0) + 1
    offer.last_boosted_at = now
    offer.expires_at = now + timedelta(minutes=30)
    db.commit()

    return {
        "boostedReward": float(offer.bounty_value),
        "newExpiry": offer.expires_at.isoformat() if offer.expires_at else None,
        "boostCount": int(offer.boost_count or 0),
    }

@router.get("/{offer_id}/competitors")
def get_offer_competitors(offer_id: str):
    return {"total_claimants": 3, "fastest_completion_estimated": 4, "your_current_distance": 800}
