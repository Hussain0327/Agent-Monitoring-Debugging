"""In-memory token-bucket rate limiter by client IP."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from vigil_server.config import settings


class _Bucket:
    __slots__ = ("tokens", "last_refill")

    def __init__(self, capacity: int) -> None:
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token-bucket rate limiter keyed by client IP.

    Configuration is read from ``settings.rate_limit_requests`` (bucket
    capacity) and ``settings.rate_limit_window_seconds`` (refill window).
    """

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self._capacity = settings.rate_limit_requests
        self._window = settings.rate_limit_window_seconds
        self._rate = self._capacity / self._window
        self._buckets: dict[str, _Bucket] = defaultdict(lambda: _Bucket(self._capacity))

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        bucket = self._buckets[client_ip]

        now = time.monotonic()
        elapsed = now - bucket.last_refill
        bucket.tokens = min(self._capacity, bucket.tokens + elapsed * self._rate)
        bucket.last_refill = now

        if bucket.tokens < 1:
            retry_after = int((1 - bucket.tokens) / self._rate) + 1
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests"},
                headers={"Retry-After": str(retry_after)},
            )

        bucket.tokens -= 1
        return await call_next(request)
