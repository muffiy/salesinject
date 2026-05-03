import uuid
from celery import chain, shared_task
from sqlalchemy.orm import Session

from ..core.ws_manager import manager
from ..database import SessionLocal
from ..models import OfferClaim
from ..services.mission_service import (
    claim_mission,
    check_geofence,
    resolve_competition,
    finalize_mission,
    mark_ai_reviewed,
)
from ..services.payout_service import calculate_payout


def _db() -> Session:
    return SessionLocal()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def task_claim_mission(self, user_id: str, offer_id: str):
    db = _db()
    try:
        claim = claim_mission(db, user_id, offer_id)
        manager.broadcast_nowait(f"🔥 New mission claimed by user {user_id}")
        return str(claim.id)
    finally:
        db.close()


@shared_task(bind=True)
def task_check_geofence(self, claim_id: str, lat: float, lon: float):
    db = _db()
    try:
        arrived = check_geofence(db, claim_id, lat, lon)
        return {"status": "arrived" if arrived else "not_arrived"}
    finally:
        db.close()


@shared_task(bind=True)
def task_submit_mission(self, claim_id: str, file_url: str):
    chain(
        task_validate_video.s(claim_id, file_url),
        task_ai_review.s(),
        task_competition_resolution.s(),
        task_calculate_payout.s(),
        task_finalize_mission.s(),
    ).apply_async()
    return {"status": "processing"}


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def task_validate_video(self, claim_id: str, file_url: str):
    db = _db()
    try:
        claim = db.query(OfferClaim).filter_by(id=claim_id).first()
        if not claim or claim.status != "submitted":
            raise ValueError("Mission must be submitted before validation")
        return {"claim_id": claim_id, "file_url": file_url}
    finally:
        db.close()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def task_ai_review(self, data: dict):
    db = _db()
    try:
        mark_ai_reviewed(db, data["claim_id"])
    finally:
        db.close()
    data["ai_score"] = 0.85
    return data


@shared_task(bind=True)
def task_competition_resolution(self, data: dict):
    db = _db()
    try:
        data.update(resolve_competition(db, data["claim_id"]))
        return data
    finally:
        db.close()


@shared_task(bind=True)
def task_calculate_payout(self, data: dict):
    data["payout"] = calculate_payout(data["claim_id"], data.get("position") == 1, data.get("ai_score", 1.0))
    return data


@shared_task(bind=True)
def task_finalize_mission(self, data: dict):
    db = _db()
    try:
        finalize_mission(db, data["claim_id"], data["payout"], data.get("position", 1))
        manager.broadcast_nowait(f"💰 Mission completed +{data['payout']} TND")
        return {"status": "completed", "payout": data["payout"]}
    finally:
        db.close()


@shared_task(bind=True)
def resolve_competition_async(self, offer_id: str):
    db = _db()
    try:
        offer_uuid = uuid.UUID(offer_id)
        claims = db.query(OfferClaim).filter(OfferClaim.offer_id == offer_uuid, OfferClaim.completed_at.isnot(None)).order_by(OfferClaim.completed_at.asc()).all()
        for idx, claim in enumerate(claims):
            claim.position = idx + 1
        db.commit()
        return {"offer_id": offer_id, "resolved": len(claims)}
    finally:
        db.close()
