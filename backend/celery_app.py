from celery import Celery
from config import settings

celery_app = Celery(
    settings.api_tittle.lower().replace(" ", "_"),
    broker=settings.celery_broker,
    backend=settings.celery_backend,
    include=[
        "tasks.parse_repository",
        "tasks.generate_embeddings",
        "tasks.import_github",
        "tasks.extract_call_graph",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.task_time_limit,
    task_soft_time_limit=settings.task_soft_time_limit,
    worker_prefetch_multiplier=1,
)

celery_app.conf.task_routes = {
    "tasks.parse_repository.*": {"queue": "parsing"},
    "tasks.generate_embeddings.*": {"queue": "embeddings"},
    "tasks.import_github.*": {"queue": "default"},
    "tasks.extract_call_graph.*": {"queue": "default"},
}
