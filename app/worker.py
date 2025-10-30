import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery = Celery(
    "reconnect_celery",
    broker=REDIS_URL,
    backend=REDIS_URL,
)
celery.conf.task_routes = {"app.tasks.*": {"queue": "reconnect"}}
