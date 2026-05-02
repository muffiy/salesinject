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
    include=["app.tasks", "app.agent_os.nodes"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Keep results for 1 hour so the status endpoint can read them
    result_expires=3600,
    # Task routing for Agent OS v2
    task_routes={
        # General tasks (existing)
        "app.tasks.*": {"queue": "general"},

        # Agent OS v2 nodes
        "app.agent_os.nodes.scout_*": {"queue": "scout"},
        "app.agent_os.nodes.hermes_*": {"queue": "core"},
        "app.agent_os.nodes.paperclip_*": {"queue": "ammo"},
        "app.agent_os.nodes.ammo_*": {"queue": "ammo"},
        "app.agent_os.nodes.content_*": {"queue": "ammo"},
        "app.agent_os.nodes.matchmaker_*": {"queue": "bounty"},
        "app.agent_os.nodes.contract_*": {"queue": "bounty"},
        "app.agent_os.nodes.bounty_*": {"queue": "bounty"},
        "app.agent_os.nodes.map_*": {"queue": "fast"},
        "app.agent_os.nodes.notification_*": {"queue": "fast"},
        "app.agent_os.nodes.cache_*": {"queue": "fast"},

        # Default routing for other agent_os nodes
        "app.agent_os.nodes.*": {"queue": "core"},
    },
    # Queue definitions
    task_queues={
        "general": {"exchange": "general", "routing_key": "general"},
        "scout": {"exchange": "scout", "routing_key": "scout"},
        "core": {"exchange": "core", "routing_key": "core"},
        "ammo": {"exchange": "ammo", "routing_key": "ammo"},
        "bounty": {"exchange": "bounty", "routing_key": "bounty"},
        "fast": {"exchange": "fast", "routing_key": "fast"},
    },
)
