"""Custom exception hierarchy and global FastAPI error handlers.

Usage::

    from vigil_server.exceptions import NotFoundError, register_error_handlers

    # In route handler
    raise NotFoundError("Trace", trace_id)

    # In app startup
    register_error_handlers(app)
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("vigil_server.exceptions")


class VigilError(Exception):
    """Base exception for all Vigil server errors."""

    def __init__(self, message: str, status_code: int = 500, detail: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail


class NotFoundError(VigilError):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            message=f"{resource} '{identifier}' not found",
            status_code=404,
        )
        self.resource = resource
        self.identifier = identifier


class ValidationError(VigilError):
    """Raised when input validation fails."""

    def __init__(self, message: str, detail: Any = None) -> None:
        super().__init__(message=message, status_code=422, detail=detail)


class AuthenticationError(VigilError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message=message, status_code=401)


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers that return structured JSON."""

    @app.exception_handler(VigilError)
    async def vigil_error_handler(request: Request, exc: VigilError) -> JSONResponse:
        logger.warning("VigilError: %s (status=%d)", exc.message, exc.status_code)
        body: dict[str, Any] = {"error": exc.message}
        if exc.detail is not None:
            body["detail"] = exc.detail
        return JSONResponse(status_code=exc.status_code, content=body)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )
