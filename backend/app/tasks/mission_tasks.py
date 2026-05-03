from celery import chain, shared_task
from sqlalchemy.orm import Session

from ..core.ws_manager import manager
from ..database import SessionLocal
from ..services.mission_service import claim_mission, start_mission, check_geofence, resolve_competition, finalize_mission
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
def task_start_mission(self, claim_id: str):
    db = _db()
    try:
        start_mission(db, claim_id)
        return {"status": "IN_PROGRESS"}
    finally:
        db.close()


@shared_task(bind=True)
def task_check_geofence(self, claim_id: str, lat: float, lon: float):
    db = _db()
    try:
        arrived = check_geofence(db, claim_id, lat, lon)
        if arrived:
            manager.broadcast_nowait("📍 User entered target zone")
            return {"status": "ARRIVED"}
        return {"status": "NOT_ARRIVED"}
    finally:
        db.close()


@shared_task(bind=True)
def task_submit_mission(self, claim_id: str, file_url: str):
    chain(task_validate_video.s(claim_id, file_url), task_ai_review.s(), task_competition_resolution.s(), task_calculate_payout.s(), task_finalize_mission.s()).apply_async()
    return {"status": "PROCESSING"}


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def task_validate_video(self, claim_id: str, file_url: str):
    return {"claim_id": claim_id, "file_url": file_url}


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def task_ai_review(self, data: dict):
    data["ai_score"] = 0.85
    return data


@shared_task(bind=True)
def task_competition_resolution(self, data: dict):
    db = _db()
    try:
        result = resolve_competition(db, data["claim_id"])
        data.update(result)
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
        return {"status": "COMPLETED", "payout": data["payout"]}
    finally:
        db.close()
