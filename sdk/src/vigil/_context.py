"""ContextVar-based trace and span propagation.

Thread-safe and async-safe via Python's contextvars module.
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vigil._types import Span, Trace

_current_trace: ContextVar[Trace | None] = ContextVar("vigil_current_trace", default=None)
_current_span: ContextVar[Span | None] = ContextVar("vigil_current_span", default=None)


def get_current_trace() -> Trace | None:
    return _current_trace.get()


def set_current_trace(trace: Trace | None) -> None:
    _current_trace.set(trace)


def get_current_span() -> Span | None:
    return _current_span.get()


def set_current_span(span: Span | None) -> None:
    _current_span.set(span)
