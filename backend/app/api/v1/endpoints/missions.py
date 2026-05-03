import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...deps import get_db, get_current_user
from ....models import OfferClaim, MissionShare, User
from ....services.mission_service import claim_mission, submit_mission, boost_mission as boost_mission_service
from ....tasks.mission_tasks import resolve_competition_async

router = APIRouter()


def _parse_uuid(value: str, field: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid {field} format") from exc


@router.post('/{offer_id}/claim')
def claim_offer_mission(offer_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        claim = claim_mission(db, str(current_user.id), offer_id)
        return {"claim_id": str(claim.id), "status": claim.status}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/{claim_id}/submit')
def submit_claim_mission(claim_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    claim_uuid = _parse_uuid(claim_id, "claim_id")
    claim = db.query(OfferClaim).filter(OfferClaim.id == claim_uuid, OfferClaim.influencer_id == current_user.id).first()
    if not claim:
        raise HTTPException(status_code=404, detail='Claim not found')
    try:
        updated = submit_mission(db, claim_id)
        return {"claim_id": str(updated.id), "status": updated.status}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/{claim_id}/boost')
def boost_mission(claim_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    claim_uuid = _parse_uuid(claim_id, "claim_id")
    claim = db.query(OfferClaim).filter(OfferClaim.id == claim_uuid, OfferClaim.influencer_id == current_user.id).first()
    if not claim:
        raise HTTPException(status_code=404, detail='Claim not found')
    updated = boost_mission_service(db, claim_id)
    if updated.status in ('completed', 'paid'):
        return {'status': 'already_done', 'newReward': float(updated.payout_amount or 0)}
    return {'claimId': claim_id, 'boosted': True, 'reviewMode': 'strict'}


@router.post('/{offer_id}/resolve')
def resolve_offer_competition(offer_id: str):
    offer_uuid = _parse_uuid(offer_id, "offer_id")
    resolve_competition_async.delay(str(offer_uuid))
    return {'status': 'queued'}


@router.post('/share/{mission_id}')
def share_mission(mission_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mission_uuid = _parse_uuid(mission_id, "mission_id")
    existing = db.query(MissionShare).filter(MissionShare.user_id == current_user.id, MissionShare.mission_id == mission_uuid).first()
    if existing:
        return {'missionId': mission_id, 'bonus': 0, 'granted': False}
    share = MissionShare(user_id=current_user.id, mission_id=mission_uuid, bonus_granted=True)
    db.add(share)
    db.commit()
    return {'missionId': mission_id, 'bonus': 2, 'granted': True}
