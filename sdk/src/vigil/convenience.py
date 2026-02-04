"""High-level convenience functions for common instrumentation tasks.

All functions no-op gracefully when no Vigil client is active, so they are
safe to sprinkle throughout application code without guarding.
"""

from __future__ import annotations

from typing import Any

from vigil._client import get_client
from vigil._context import get_current_span, get_current_trace
from vigil._types import SpanKind, SpanStatus


def log_event(name: str, attributes: dict[str, Any] | None = None) -> None:
    """Add an event to the current span.

    No-ops if there is no active client or span.
    """
    client = get_client()
    if not client:
        return
    span = get_current_span()
    if span:
        span.add_event(name, attributes)


def attach_metadata(key: str, value: Any) -> None:
    """Attach a key/value to the current span or trace metadata.

    Prefers the current span; falls back to the current trace.
    No-ops if there is no active client or context.
    """
    client = get_client()
    if not client:
        return
    span = get_current_span()
    if span:
        span.metadata[key] = value
        return
    trace = get_current_trace()
    if trace:
        trace.metadata[key] = value


def log_llm_call(
    model: str,
    input: dict[str, Any] | None = None,
    output: dict[str, Any] | None = None,
) -> None:
    """Create and immediately end an LLM span.

    Useful for wrapping LLM calls that don't use the ``@span`` decorator.
    No-ops if there is no active client.
    """
    client = get_client()
    if not client:
        return
    s = client.start_span(f"llm:{model}", kind=SpanKind.LLM, input=input)
    client.end_span_sync(s, status=SpanStatus.OK, output=output)


def log_tool_call(
    tool_name: str,
    input: dict[str, Any] | None = None,
    output: dict[str, Any] | None = None,
) -> None:
    """Create and immediately end a TOOL span.

    Useful for wrapping tool invocations that don't use the ``@span`` decorator.
    No-ops if there is no active client.
    """
    client = get_client()
    if not client:
        return
    s = client.start_span(f"tool:{tool_name}", kind=SpanKind.TOOL, input=input)
    client.end_span_sync(s, status=SpanStatus.OK, output=output)
