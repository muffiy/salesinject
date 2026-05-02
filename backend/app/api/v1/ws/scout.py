import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import redis
from app.core.config import settings

router = APIRouter()
r = redis.Redis.from_url(settings.REDIS_URL)


@router.websocket("/ws/scout/{task_id}")
async def scout_ws(websocket: WebSocket, task_id: str):
    await websocket.accept()
    pubsub = r.pubsub()
    pubsub.subscribe(f"task:{task_id}")
    try:
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                await websocket.send_json(json.loads(message["data"]))
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pubsub.close()
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
        pubsub.close()