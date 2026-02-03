"""VigilClient manages the SDK lifecycle: init, tracing, and shutdown."""

from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any

from vigil._config import SDKConfig
from vigil._context import (
    get_current_span,
    get_current_trace,
    set_current_span,
    set_current_trace,
)
from vigil._exporter import BatchSpanExporter
from vigil._types import Span, SpanKind, SpanStatus, Trace

logger = logging.getLogger("vigil")

_global_client: VigilClient | None = None
_global_lock = threading.Lock()


class VigilClient:
    """Core client that manages trace/span lifecycle and export."""

    def __init__(self, config: SDKConfig) -> None:
        self._config = config
        self._exporter = BatchSpanExporter(config)
        self._started = False

    @property
    def config(self) -> SDKConfig:
        """Return the SDK configuration."""
        return self._config

    @property
    def is_started(self) -> bool:
        """Return whether the client has been started."""
        return self._started

    async def start(self) -> None:
        """Start the client and begin exporting spans."""
        if self._started:
            return
        await self._exporter.start()
        self._started = True
        logger.info("Vigil SDK started (endpoint=%s)", self._config.endpoint)

    async def shutdown(self) -> None:
        """Flush remaining spans and shut down the client."""
        if not self._started:
            return
        await self._exporter.stop()
        self._started = False
        logger.info("Vigil SDK shut down")

    # -- tracing -------------------------------------------------------------

    def start_trace(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> Trace:
        """Create a new trace and set it as the current trace."""
        trace = Trace(
            name=name,
            project_id=self._config.project_id,
            metadata=metadata or {},
        )
        set_current_trace(trace)
        return trace

    def end_trace(self, trace: Trace | None = None) -> None:
        """End a trace and clear it from the context."""
        t = trace or get_current_trace()
        if t:
            t.end()
            set_current_trace(None)

    def start_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.CUSTOM,
        input: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Span:
        """Create a new span linked to the current trace and parent span."""
        trace = get_current_trace()
        parent = get_current_span()

        span = Span(
            name=name,
            trace_id=trace.trace_id if trace else "",
            parent_span_id=parent.span_id if parent else None,
            kind=kind,
            input=input,
            metadata=metadata or {},
        )

        if trace:
            trace.spans.append(span)
        set_current_span(span)
        return span

    async def end_span(
        self,
        span: Span | None = None,
        status: SpanStatus = SpanStatus.OK,
        output: dict[str, Any] | None = None,
    ) -> None:
        """End a span asynchronously and export it."""
        s = span or get_current_span()
        if not s:
            return
        s.end(status=status)
        if output:
            s.set_output(output)
        if self._started:
            await self._exporter.export(s)
        set_current_span(None)

    def end_span_sync(
        self,
        span: Span | None = None,
        status: SpanStatus = SpanStatus.OK,
        output: dict[str, Any] | None = None,
    ) -> None:
        """End a span synchronously using the thread-safe sync queue.

        This avoids the ``asyncio.get_event_loop().run_until_complete()``
        anti-pattern that fails when an event loop is already running.
        """
        s = span or get_current_span()
        if not s:
            return
        s.end(status=status)
        if output:
            s.set_output(output)
        if self._started:
            self._exporter.enqueue_sync(s)
        set_current_span(None)

    async def flush(self) -> None:
        """Flush all pending spans to the server."""
        await self._exporter.flush()


def get_client() -> VigilClient | None:
    """Return the global client instance, or ``None`` if not initialised."""
    with _global_lock:
        return _global_client


def _set_client(client: VigilClient | None) -> None:
    """Set the global client instance (thread-safe)."""
    global _global_client
    with _global_lock:
        _global_client = client


async def init(
    endpoint: str = "http://localhost:8000",
    api_key: str = "",
    project_id: str = "default",
    **kwargs: Any,
) -> VigilClient:
    """Initialize the Vigil SDK globally.

    Returns the client instance for manual lifecycle management.
    """
    config = SDKConfig(
        endpoint=endpoint,
        api_key=api_key,
        project_id=project_id,
        **kwargs,
    )
    client = VigilClient(config)
    await client.start()
    _set_client(client)
    return client


async def shutdown() -> None:
    """Shut down the global Vigil client."""
    client = get_client()
    if client:
        await client.shutdown()
        _set_client(None)
