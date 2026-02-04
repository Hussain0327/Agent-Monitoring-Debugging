"""Vigil: observability SDK for AI agent pipelines.

Usage:
    import vigil

    # Initialize
    await vigil.init(endpoint="http://localhost:8000", api_key="...")

    # Decorators
    @vigil.trace()
    async def my_pipeline():
        ...

    @vigil.span(kind=vigil.SpanKind.LLM)
    async def call_llm():
        ...

    # Context manager
    async with vigil.trace_context(client, "my-trace") as t:
        ...

    # Convenience functions
    vigil.log_event("cache-hit", {"key": "abc"})
    vigil.log_llm_call("gpt-4", input={...}, output={...})
    vigil.log_tool_call("search", input={...}, output={...})
    vigil.attach_metadata("user_id", "u123")

    # Manual
    span = vigil.current_span()

    # Shutdown
    await vigil.shutdown()
"""

from vigil._client import get_client, init, shutdown
from vigil._context import get_current_span as current_span
from vigil._context import get_current_trace as current_trace
from vigil._trace_context import TraceContext
from vigil._types import Event, Span, SpanKind, SpanStatus, Trace
from vigil.convenience import attach_metadata, log_event, log_llm_call, log_tool_call
from vigil.decorators import span, trace
from vigil.integrations import activate as activate_integration
from vigil.integrations import activate_all as activate_all_integrations
from vigil.integrations import available as available_integrations

# Public alias matching the documented API (lowercase for context-manager usage)
trace_context = TraceContext

__all__ = [
    "init",
    "shutdown",
    "get_client",
    "trace",
    "span",
    "trace_context",
    "TraceContext",
    "current_span",
    "current_trace",
    "Trace",
    "Span",
    "Event",
    "SpanKind",
    "SpanStatus",
    "log_event",
    "attach_metadata",
    "log_llm_call",
    "log_tool_call",
    "activate_integration",
    "activate_all_integrations",
    "available_integrations",
]
