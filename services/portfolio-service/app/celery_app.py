"""
Celery application configuration
"""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "portfolio_service",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.REDIS_URL,
    include=["app.celery_tasks.price_updates"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    "update-prices-every-hour": {
        "task": "app.celery_tasks.price_updates.update_all_prices",
        "schedule": 3600.0,  # Every hour
    },
}
