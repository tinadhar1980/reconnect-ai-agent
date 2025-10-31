import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Redis broker and backend
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery = Celery(
    "reconnect_ai",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"],  
)

celery.conf.task_routes = {
    "app.tasks.process_checkout": {"queue": "checkout"},
    "app.tasks.evaluate_reconnect_offer": {"queue": "analysis"},
}

celery.conf.update(
    task_default_retry_delay=10,  
    task_time_limit=300,
    worker_concurrency=2,
)
