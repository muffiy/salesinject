import asyncio
import random
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

EVENTS = [
    ('influencer_earned', 'Yassine just earned +12 TND'),
    ('mission_competing', '3 people competing for this mission'),
    ('hot_drop_nearby', 'New HOT drop nearby (+25%)'),
]

@router.websocket('/ws/live-ticker')
async def live_ticker(websocket: WebSocket):
    await websocket.accept()
    try:
      while True:
        ev, msg = random.choice(EVENTS)
        await websocket.send_json({'event': ev, 'message': msg})
        await asyncio.sleep(3)
    except WebSocketDisconnect:
      return

@router.websocket('/ws/offer/{offer_id}/activity')
async def offer_activity(websocket: WebSocket, offer_id: str):
    await websocket.accept()
    base = 900
    try:
      while True:
        competitors = random.randint(2, 5)
        base = max(50, base - random.randint(10, 40))
        await websocket.send_json({
          'offer_id': offer_id,
          'competitors': competitors,
          'estimated_arrival_min': random.randint(3, 7),
          'your_arrival_min': random.randint(4, 9),
          'your_current_distance': base,
        })
        await asyncio.sleep(2)
    except WebSocketDisconnect:
      return
