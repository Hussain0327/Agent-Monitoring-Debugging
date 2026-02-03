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

    # Manual
    span = vigil.current_span()

    # Shutdown
    await vigil.shutdown()
"""

from vigil._client import get_client, init, shutdown
from vigil._context import get_current_span as current_span
from vigil._context import get_current_trace as current_trace
from vigil._types import Event, Span, SpanKind, SpanStatus, Trace
from vigil.decorators import span, trace

__all__ = [
    "init",
    "shutdown",
    "get_client",
    "trace",
    "span",
    "current_span",
    "current_trace",
    "Trace",
    "Span",
    "Event",
    "SpanKind",
    "SpanStatus",
]
