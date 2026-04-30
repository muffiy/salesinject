from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "salesinject_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,  # 1 hour
)

# Periodic tasks — Celery Beat schedule
celery_app.conf.beat_schedule = {
    "expire-offers-every-15min": {
        "task": "app.tasks.expire_offers",
        "schedule": crontab(minute="*/15"),
    },
    "rebuild-leaderboard-hourly": {
        "task": "app.tasks.rebuild_leaderboard",
        "schedule": crontab(minute=0),
    },
    "update-rank-decay-daily": {
        "task": "app.tasks.rank_decay",
        "schedule": crontab(hour=3, minute=0),
    },
}
