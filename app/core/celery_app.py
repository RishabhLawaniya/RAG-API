from celery import Celery
import os

# Use environment variable — defaults to localhost for dev
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

print("REDIS_URL:", REDIS_URL)

celery_app = Celery(
    "rag_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.document_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_max_retries=3,
    task_default_retry_delay=60,
    result_expires=86400,
    worker_pool="solo",
    broker_connection_retry_on_startup=True,
)