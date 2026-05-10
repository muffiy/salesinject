import uuid
import logging
import json
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Injects trace_id per request and logs structured JSON."""

    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id

        start = datetime.now(timezone.utc)
        response: Response = await call_next(request)
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()

        log_entry = {
            "trace_id": trace_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "elapsed_seconds": round(elapsed, 4),
            "user_id": getattr(request.state, "user_id", None),
        }
        logging.getLogger("salesinject.access").info(json.dumps(log_entry))
        return response


def setup_logging() -> None:
    """Configure structured JSON logging for the application."""
    logger = logging.getLogger("salesinject")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","message":"%(message)s"}',
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    ))
    logger.addHandler(handler)
    logging.getLogger("salesinject.access").setLevel(logging.INFO)
    logging.getLogger("salesinject.access").addHandler(handler)