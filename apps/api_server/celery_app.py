"""Celery application for background tasks."""

from celery import Celery
from shared.config import get_config

config = get_config()

# Create Celery app
celery_app = Celery(
    "python-cli",
    broker=config.celery.broker_url,
    backend=config.celery.result_backend,
    include=["apps.api_server.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer=config.celery.task_serializer,
    accept_content=config.celery.accept_content,
    result_serializer=config.celery.result_serializer,
    timezone=config.celery.timezone,
    enable_utc=config.celery.enable_utc,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["apps.api_server"])


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f"Request: {self.request!r}")
    return "Debug task completed"


if __name__ == "__main__":
    celery_app.start()