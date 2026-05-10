"""Simple in-memory rate limiter for FastAPI endpoints.

Usage:
    @router.post("/endpoint")
    @rate_limit(max_requests=5, window_seconds=60)
    async def my_endpoint(request: Request):
        ...
"""
import time
from functools import wraps
from fastapi import Request, HTTPException


class _MemoryStore:
    """In-memory rate limit store."""

    def __init__(self):
        self._buckets: dict[str, list[float]] = {}

    def check(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        timestamps = self._buckets.get(key, [])
        timestamps = [t for t in timestamps if now - t < window_seconds]
        if len(timestamps) >= max_requests:
            self._buckets[key] = timestamps
            return False
        timestamps.append(now)
        self._buckets[key] = timestamps
        return True


_store = _MemoryStore()


def _get_request(args, kwargs):
    for arg in args:
        if isinstance(arg, Request):
            return arg
    for v in kwargs.values():
        if isinstance(v, Request):
            return v
    return None


def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """Decorator that rate-limits an endpoint by client IP."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            request = _get_request(args, kwargs)
            if request:
                client_ip = request.client.host if request.client else "unknown"
                key = f"ratelimit:{func.__name__}:{client_ip}"
                if not _store.check(key, max_requests, window_seconds):
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Max {max_requests} per {window_seconds}s.",
                    )
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            request = _get_request(args, kwargs)
            if request:
                client_ip = request.client.host if request.client else "unknown"
                key = f"ratelimit:{func.__name__}:{client_ip}"
                if not _store.check(key, max_requests, window_seconds):
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Max {max_requests} per {window_seconds}s.",
                    )
            return func(*args, **kwargs)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator