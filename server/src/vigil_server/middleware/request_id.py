"""Request-ID middleware.

Assigns a unique request ID to every incoming request so that all log
entries emitted during that request can be correlated.  The ID is read
from the ``X-Request-ID`` header if present, otherwise a UUID is
generated.  It is stored in a :class:`~contextvars.ContextVar` and
added to the response headers.
"""

from __future__ import annotations

import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    """Return the current request ID, or ``None`` outside a request context."""
    return _request_id_ctx.get()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that propagates or generates an ``X-Request-ID``."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        _request_id_ctx.set(request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
