"""
FastAPI router for AI hub endpoints: intent classification, recommendation, and generation.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import json
from celery.result import AsyncResult
from app.core.redis import get_redis
from redis import Redis

from app.ai_hub.tasks import classify_intent_task, recommend_task, generate_task

router = APIRouter(prefix="/ai", tags=["AI"])


class IntentRequest(BaseModel):
    text: str
    user_id: str
    async_: Optional[bool] = False  # using async_ to avoid conflict with Python keyword


class IntentResponse(BaseModel):
    intent: str
    confidence: float
    task_id: Optional[str] = None


class RecommendRequest(BaseModel):
    context: str
    user_id: str
    async_: Optional[bool] = False


class RecommendResponse(BaseModel):
    recommendations: list
    task_id: Optional[str] = None


class GenerateRequest(BaseModel):
    prompt: str
    user_id: str
    params: Optional[Dict[str, Any]] = None
    async_: Optional[bool] = False


class GenerateResponse(BaseModel):
    generated: str
    task_id: Optional[str] = None


@router.post("/intent", response_model=IntentResponse)
async def classify_intent(
    request: IntentRequest,
    background_tasks: BackgroundTasks,
    redis: Redis = Depends(get_redis),
):
    """
    Classify the intent of the given text.
    If async_=True, returns a task ID and processes in background.
    If async_=False (default), waits for result and returns immediately.
    """
    if request.async_:
        # Launch task asynchronously
        task = classify_intent_task.delay(request.user_id, request.text)
        # Store initial status in Redis (optional, for tracking)
        redis.setex(f"ai_task:{task.id}", 3600, json.dumps({"status": "PENDING"}))
        return IntentResponse(
            intent="processing",
            confidence=0.0,
            task_id=task.id,
        )
    else:
        # Process synchronously
        result = classify_intent_task(request.user_id, request.text)
        return IntentResponse(
            intent=result["intent"],
            confidence=result["confidence"],
        )


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(
    request: RecommendRequest,
    background_tasks: BackgroundTasks,
    redis: Redis = Depends(get_redis),
):
    """
    Generate recommendations based on context.
    If async_=True, returns a task ID and processes in background.
    If async_=False (default), waits for result and returns immediately.
    """
    if request.async_:
        task = recommend_task.delay(request.user_id, request.context)
        redis.setex(f"ai_task:{task.id}", 3600, json.dumps({"status": "PENDING"}))
        return RecommendResponse(
            recommendations=[],
            task_id=task.id,
        )
    else:
        result = recommend_task(request.user_id, request.context)
        return RecommendResponse(
            recommendations=result["recommendations"],
        )


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    redis: Redis = Depends(get_redis),
):
    """
    Generate content based on prompt.
    If async_=True, returns a task ID and processes in background.
    If async_=False (default), waits for result and returns immediately.
    """
    if request.async_:
        task = generate_task.delay(request.user_id, request.prompt, request.params or {})
        redis.setex(f"ai_task:{task.id}", 3600, json.dumps({"status": "PENDING"}))
        return GenerateResponse(
            generated="processing",
            task_id=task.id,
        )
    else:
        result = generate_task(request.user_id, request.prompt, request.params or {})
        return GenerateResponse(
            generated=result["generated"],
        )


# Optional: endpoint to check task status
@router.get("/task/{task_id}")
async def get_task_status(task_id: str, redis: Redis = Depends(get_redis)):
    """
    Get the status and result of an AI task by task ID.
    """
    # Check Redis first for cached status
    cached = redis.get(f"ai_task:{task_id}")
    if cached:
        data = json.loads(cached)
        if data.get("status") in ["SUCCESS", "FAILURE"]:
            return data

    # Fallback to Celery result
    result = AsyncResult(task_id, app=router.app.celery_app if hasattr(router.app, 'celery_app') else None)
    if result.ready():
        if result.successful():
            return {"status": "SUCCESS", "result": result.result}
        else:
            return {"status": "FAILURE", "error": str(result.result)}
    else:
        return {"status": "PENDING"}