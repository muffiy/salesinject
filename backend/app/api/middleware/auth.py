import os
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

PUBLIC_PATHS = {
    "/health",
    "/api/v1/health",
    "/api/v1/health/",
    "/api/v1/auth/password-login",
    "/api/v1/telegram/webhook",
    "/docs",
    "/openapi.json",
    "/metrics",
}


class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    """Validates X-API-Key header for non-public endpoints.

    Only active when INTERNAL_API_KEY env var is set.
    """

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path.rstrip("/")
        if path in PUBLIC_PATHS or any(
            path.startswith(p) for p in ["/docs", "/openapi", "/redoc"]
        ):
            return await call_next(request)

        expected = os.getenv("INTERNAL_API_KEY", "")
        if expected:
            provided = request.headers.get("X-API-Key", "")
            if provided != expected:
                return JSONResponse(
                    status_code=401, content={"detail": "Invalid or missing API key"}
                )

        return await call_next(request)