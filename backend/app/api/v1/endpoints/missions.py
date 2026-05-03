from fastapi import APIRouter

router = APIRouter()

@router.post('/{claim_id}/boost')
def boost_mission(claim_id: str, reward: float = 15.0):
    return {'claimId': claim_id, 'newReward': round(reward * 1.3, 2), 'reviewMode': 'strict'}

@router.post('/share/{mission_id}')
def share_mission(mission_id: str):
    return {'missionId': mission_id, 'bonus': 2, 'granted': True}

@router.post('/re-run/{trace_id}')
def rerun_mission(trace_id: str):
    return {'trace_id': trace_id, 'boosted_reward_multiplier': 1.2, 'redirect': f'/mission/{trace_id}'}
