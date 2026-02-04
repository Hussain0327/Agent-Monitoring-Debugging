"""Tests for the TraceContext context manager."""

from __future__ import annotations

import pytest

from vigil._client import VigilClient, _set_client
from vigil._config import SDKConfig
from vigil._context import get_current_trace, set_current_span, set_current_trace
from vigil._trace_context import TraceContext


@pytest.fixture
def client():
    """Provide a VigilClient and register it globally."""
    config = SDKConfig(endpoint="http://test:8000", api_key="test", enabled=False)
    c = VigilClient(config)
    c._started = True
    _set_client(c)
    yield c
    _set_client(None)
    set_current_span(None)
    set_current_trace(None)


class TestSyncContextManager:
    def test_creates_and_ends_trace(self, client):
        with TraceContext(client, "sync-test") as trace:
            assert trace.name == "sync-test"
            assert trace.end_time is None
        assert trace.end_time is not None

    def test_success_sets_no_error(self, client):
        with TraceContext(client, "success-test") as trace:
            pass
        assert trace.status != "error"

    def test_error_sets_error_status(self, client):
        try:
            with TraceContext(client, "error-test") as trace:
                raise ValueError("boom")
        except ValueError:
            pass
        assert trace.status == "error"

    def test_exception_propagates(self, client):
        with pytest.raises(ValueError, match="boom"):
            with TraceContext(client, "propagation-test"):
                raise ValueError("boom")

    def test_clears_context_on_exit(self, client):
        with TraceContext(client, "ctx-test"):
            pass
        assert get_current_trace() is None

    def test_metadata_passed(self, client):
        with TraceContext(client, "meta-test", metadata={"k": "v"}) as trace:
            assert trace.metadata == {"k": "v"}


class TestAsyncContextManager:
    @pytest.mark.asyncio
    async def test_creates_and_ends_trace(self, client):
        async with TraceContext(client, "async-test") as trace:
            assert trace.name == "async-test"
            assert trace.end_time is None
        assert trace.end_time is not None

    @pytest.mark.asyncio
    async def test_error_sets_error_status(self, client):
        try:
            async with TraceContext(client, "async-error") as trace:
                raise RuntimeError("async boom")
        except RuntimeError:
            pass
        assert trace.status == "error"

    @pytest.mark.asyncio
    async def test_exception_propagates(self, client):
        with pytest.raises(RuntimeError, match="async boom"):
            async with TraceContext(client, "async-propagation"):
                raise RuntimeError("async boom")

    @pytest.mark.asyncio
    async def test_clears_context_on_exit(self, client):
        async with TraceContext(client, "async-ctx"):
            pass
        assert get_current_trace() is None
