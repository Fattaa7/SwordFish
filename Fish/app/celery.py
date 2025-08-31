from celery import Celery
from app.core.config import settings  # your .env loader

celery_app = Celery(
    "swordfish",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1"
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


celery_app.autodiscover_tasks(["app.tasks"])
