"""
Celery application factory for SalesInject.

All tasks are defined in `app.tasks` and auto-discovered from here.
Broker and result backend both point at Redis (configured in .env).
"""
from celery import Celery
from .core.config import settings

celery_app = Celery(
    "salesinject",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Keep results for 1 hour so the status endpoint can read them
    result_expires=3600,
)
