"""Celery tasks for the API server."""

import time
from typing import Dict, Any
from celery import current_task
from .celery_app import celery_app
from shared.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(bind=True)
def sample_task(self, name: str) -> Dict[str, Any]:
    """Sample background task."""
    logger.info(f"Starting sample task for {name}")
    
    # Simulate some work
    for i in range(10):
        time.sleep(1)
        current_task.update_state(
            state="PROGRESS",
            meta={"current": i + 1, "total": 10, "status": f"Processing {name}..."}
        )
    
    result = {
        "name": name,
        "status": "completed",
        "message": f"Task for {name} completed successfully"
    }
    
    logger.info(f"Completed sample task for {name}")
    return result


@celery_app.task
def send_email_task(to: str, subject: str, body: str) -> Dict[str, Any]:
    """Send email task (mock implementation)."""
    logger.info(f"Sending email to {to}")
    
    # Mock email sending
    time.sleep(2)
    
    result = {
        "to": to,
        "subject": subject,
        "status": "sent",
        "message": "Email sent successfully"
    }
    
    logger.info(f"Email sent to {to}")
    return result


@celery_app.task
def cleanup_old_data() -> Dict[str, Any]:
    """Cleanup old data task."""
    logger.info("Starting cleanup task")
    
    # Mock cleanup
    time.sleep(5)
    
    result = {
        "status": "completed",
        "cleaned_items": 42,
        "message": "Old data cleaned up successfully"
    }
    
    logger.info("Cleanup task completed")
    return result


@celery_app.task(bind=True)
def long_running_task(self, duration: int = 60) -> Dict[str, Any]:
    """Long running task with progress updates."""
    logger.info(f"Starting long running task for {duration} seconds")
    
    for i in range(duration):
        time.sleep(1)
        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": i + 1,
                "total": duration,
                "status": f"Processing... {i + 1}/{duration}"
            }
        )
    
    result = {
        "status": "completed",
        "duration": duration,
        "message": f"Long running task completed after {duration} seconds"
    }
    
    logger.info(f"Long running task completed after {duration} seconds")
    return result


# Periodic tasks (uncomment to enable)
# from celery.schedules import crontab
# 
# celery_app.conf.beat_schedule = {
#     'cleanup-old-data': {
#         'task': 'apps.api_server.tasks.cleanup_old_data',
#         'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
#     },
# }