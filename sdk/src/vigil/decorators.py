"""@trace and @span decorators for automatic instrumentation.

Supports both sync and async functions via ``iscoroutinefunction`` detection.
Sync wrappers use the thread-safe ``end_span_sync`` method instead of the
deprecated ``asyncio.get_event_loop().run_until_complete()`` pattern.
"""

from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, ParamSpec, TypeVar

from vigil._client import get_client
from vigil._context import get_current_span, set_current_span
from vigil._types import SpanKind, SpanStatus

P = ParamSpec("P")
R = TypeVar("R")


def trace(
    name: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator that wraps a function in a new trace.

    Usage::

        @trace()
        async def my_pipeline():
            ...

        @trace(name="custom-name")
        def my_sync_pipeline():
            ...
    """

    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        trace_name = name or fn.__qualname__

        if inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                client = get_client()
                if not client:
                    return await fn(*args, **kwargs)  # type: ignore[misc]

                t = client.start_trace(trace_name, metadata=metadata)
                try:
                    result = await fn(*args, **kwargs)  # type: ignore[misc]
                    return result
                finally:
                    client.end_trace(t)

            return async_wrapper  # type: ignore[return-value]

        else:

            @functools.wraps(fn)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                client = get_client()
                if not client:
                    return fn(*args, **kwargs)

                t = client.start_trace(trace_name, metadata=metadata)
                try:
                    result = fn(*args, **kwargs)
                    return result
                finally:
                    client.end_trace(t)

            return sync_wrapper  # type: ignore[return-value]

    return decorator


def span(
    name: str | None = None,
    kind: SpanKind = SpanKind.CUSTOM,
    metadata: dict[str, Any] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator that wraps a function in a new span.

    Usage::

        @span(kind=SpanKind.LLM)
        async def call_llm(prompt: str):
            ...

        @span(name="parse-output")
        def parse(raw: str):
            ...
    """

    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        span_name = name or fn.__qualname__

        if inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                client = get_client()
                if not client:
                    return await fn(*args, **kwargs)  # type: ignore[misc]

                prev_span = get_current_span()
                s = client.start_span(span_name, kind=kind, metadata=metadata)
                try:
                    result = await fn(*args, **kwargs)  # type: ignore[misc]
                    await client.end_span(s, status=SpanStatus.OK)
                    return result
                except Exception:
                    await client.end_span(s, status=SpanStatus.ERROR)
                    raise
                finally:
                    set_current_span(prev_span)

            return async_wrapper  # type: ignore[return-value]

        else:

            @functools.wraps(fn)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                client = get_client()
                if not client:
                    return fn(*args, **kwargs)

                prev_span = get_current_span()
                s = client.start_span(span_name, kind=kind, metadata=metadata)
                try:
                    result = fn(*args, **kwargs)
                    client.end_span_sync(s, status=SpanStatus.OK)
                    return result
                except Exception:
                    client.end_span_sync(s, status=SpanStatus.ERROR)
                    raise
                finally:
                    set_current_span(prev_span)

            return sync_wrapper  # type: ignore[return-value]

    return decorator
