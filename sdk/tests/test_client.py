"""Tests for VigilClient lifecycle and span management."""

from __future__ import annotations

import pytest

from vigil._client import VigilClient, _set_client, get_client, init, shutdown
from vigil._config import SDKConfig
from vigil._context import get_current_span, get_current_trace, set_current_span, set_current_trace
from vigil._types import SpanKind, SpanStatus


class TestClientLifecycle:
    """Client start/shutdown works correctly."""

    async def test_start(self, client):
        assert client.is_started is True

    async def test_shutdown(self, config, mock_server):
        c = VigilClient(config)
        await c.start()
        assert c.is_started is True
        await c.shutdown()
        assert c.is_started is False

    async def test_double_start(self, client):
        # Should not raise
        await client.start()
        assert client.is_started is True

    async def test_shutdown_before_start(self, config):
        c = VigilClient(config)
        # Should not raise
        await c.shutdown()
        assert c.is_started is False


class TestGlobalClient:
    """Global client singleton works correctly."""

    async def test_init_and_get(self, mock_server):
        c = await init(
            endpoint="http://test-server:8000",
            api_key="test-key",
            project_id="test-project",
            batch_size=10,
            flush_interval_ms=100,
        )
        try:
            assert get_client() is c
            assert c.is_started is True
        finally:
            await shutdown()
            assert get_client() is None

    async def test_shutdown_without_init(self):
        _set_client(None)
        # Should not raise
        await shutdown()


class TestTracing:
    """Trace and span creation works correctly."""

    async def test_start_trace(self, client):
        trace = client.start_trace("test-trace")
        assert trace.name == "test-trace"
        assert get_current_trace() is trace
        client.end_trace(trace)
        assert get_current_trace() is None

    async def test_start_span(self, client):
        trace = client.start_trace("test-trace")
        span = client.start_span("test-span", kind=SpanKind.LLM)
        assert span.name == "test-span"
        assert span.kind == SpanKind.LLM
        assert span.trace_id == trace.trace_id
        assert get_current_span() is span
        await client.end_span(span, status=SpanStatus.OK)
        client.end_trace(trace)

    async def test_span_parent_linking(self, client):
        trace = client.start_trace("test-trace")
        parent = client.start_span("parent")
        child = client.start_span("child")
        assert child.parent_span_id == parent.span_id
        await client.end_span(child)
        await client.end_span(parent)
        client.end_trace(trace)

    async def test_end_span_sync(self, client):
        trace = client.start_trace("test-trace")
        span = client.start_span("test-span")
        client.end_span_sync(span, status=SpanStatus.OK)
        assert span.status == SpanStatus.OK
        assert span.end_time is not None
        client.end_trace(trace)

    async def test_end_span_with_output(self, client):
        trace = client.start_trace("test-trace")
        span = client.start_span("test-span")
        await client.end_span(span, status=SpanStatus.OK, output={"result": 42})
        assert span.output == {"result": 42}
        client.end_trace(trace)
