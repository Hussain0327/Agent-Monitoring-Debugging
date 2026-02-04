"""Structured JSON logging configuration.

Provides a JSON formatter and a ``configure_logging`` helper that should
be called during application startup.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any


class StructuredFormatter(logging.Formatter):
    """JSON log formatter that includes timestamp, level, logger, message,
    and an optional ``request_id`` pulled from :mod:`contextvars`.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Attach request_id if available
        try:
            from vigil_server.middleware.request_id import get_request_id

            request_id = get_request_id()
            if request_id:
                log_entry["request_id"] = request_id
        except ImportError:
            pass

        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def configure_logging(level: str = "info") -> None:
    """Configure root logging with the structured JSON formatter.

    Args:
        level: Log level name (e.g. ``"info"``, ``"debug"``).
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())

    # Quiet noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
