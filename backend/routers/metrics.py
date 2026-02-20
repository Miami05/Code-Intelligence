"""
Prometheus metrics endpoint for Sprint 10 monitoring.
"""

from fastapi import APIRouter
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.responses import Response

router = APIRouter(tags=["monitoring"])

api_requests_total = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "status_code"],
)

api_request_duration_seconds = Histogram(
    "api_request_duration_seconds",
    "API request duration in seconds",
    ["endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

cache_hits_total = Counter("cache_hits_total", "Total cache hits", ["cache_prefix"])
cache_misses_total = Counter(
    "cache_misses_total", "Total cache misses", ["cache_prefix"]
)

active_celery_tasks = Gauge(
    "active_celery_tasks",
    "Number of currently active Celery tasks",
)

repositories_total = Gauge(
    "repositories_total",
    "Total number of repositories in the system",
)


@router.get("/metrics", response_class=Response)
def metrics():
    """Expose Prometheus metrics for scraping."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
