"""Prometheus metrics for SalesInject.

Provides request counting, duration histograms, and a /metrics endpoint.
Gracefully degrades if prometheus_client is not installed.
"""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

try:
    from prometheus_client import Counter, Histogram, generate_latest, REGISTRY

    REQUEST_COUNT = Counter(
        "salesinject_requests_total",
        "Total HTTP requests",
        ["method", "path", "status_code"],
    )

    REQUEST_DURATION = Histogram(
        "salesinject_request_duration_seconds",
        "HTTP request duration in seconds",
        ["method", "path"],
        buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    )

    _PROMETHEUS_AVAILABLE = True
except ImportError:
    _PROMETHEUS_AVAILABLE = False


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Counts requests and measures duration for Prometheus metrics."""

    async def dispatch(self, request: Request, call_next):
        if not _PROMETHEUS_AVAILABLE:
            return await call_next(request)

        start = time.time()
        response = await call_next(request)
        duration = time.time() - start

        REQUEST_COUNT.labels(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        ).inc()
        REQUEST_DURATION.labels(
            method=request.method,
            path=request.url.path,
        ).observe(duration)

        return response


async def metrics_endpoint(request: Request):
    """Exposes Prometheus metrics at /metrics."""
    from fastapi.responses import PlainTextResponse
    if not _PROMETHEUS_AVAILABLE:
        return PlainTextResponse(
            "# prometheus_client not installed",
            media_type="text/plain",
            status_code=200,
        )
    return PlainTextResponse(
        generate_latest(REGISTRY),
        media_type="text/plain",
    )