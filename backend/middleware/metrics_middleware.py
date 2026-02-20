"""
Middleware to collect request metrics for Prometheus.
"""

import time

from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from routers.metrics import api_request_duration_seconds, api_requests_total


class MetricsMiddleware(BaseHTTPMiddleware):
    """Track request count and duration for all API endpoints."""

    SKIP_PATHS = {"/metrics", "/health", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)
        start_time = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start_time
        api_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=str(response.status_code),
        ).inc()
        api_request_duration_seconds.labels(endpoint=request.url.path).observe(duration)
        return response
