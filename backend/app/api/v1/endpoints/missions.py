import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...deps import get_db, get_current_user
from ....models import OfferClaim, MissionShare, User

router = APIRouter()


def _parse_uuid(value: str, field: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid {field} format") from exc


@router.post('/{claim_id}/boost')
def boost_mission(claim_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    claim_uuid = _parse_uuid(claim_id, "claim_id")
    claim = db.query(OfferClaim).filter(OfferClaim.id == claim_uuid, OfferClaim.influencer_id == current_user.id).first()
    if not claim:
        raise HTTPException(status_code=404, detail='Claim not found')
    if claim.status == 'completed':
        return {'status': 'already_done', 'newReward': float(claim.payout_amount or 0)}
    claim.boosted = True
    db.commit()
    return {'claimId': claim_id, 'boosted': True, 'reviewMode': 'strict'}


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


@router.post('/re-run/{trace_id}')
def rerun_mission(trace_id: str):
    return {'trace_id': trace_id, 'boosted_reward_multiplier': 1.2, 'redirect': f'/mission/{trace_id}'}
