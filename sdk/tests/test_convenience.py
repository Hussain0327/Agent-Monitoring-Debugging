"""Tests for convenience functions."""

from __future__ import annotations

import pytest

from vigil._client import VigilClient, _set_client
from vigil._config import SDKConfig
from vigil._context import set_current_span, set_current_trace
from vigil._types import Span, SpanKind, Trace
from vigil.convenience import attach_metadata, log_event, log_llm_call, log_tool_call


@pytest.fixture
def client():
    """Provide a VigilClient (not started) and register it globally."""
    config = SDKConfig(endpoint="http://test:8000", api_key="test", enabled=False)
    c = VigilClient(config)
    # Mark as started so span operations work through enqueue_sync
    c._started = True
    _set_client(c)
    yield c
    _set_client(None)
    set_current_span(None)
    set_current_trace(None)


class TestLogEvent:
    def test_log_event_with_active_span(self, client):
        span = Span(name="test-span")
        set_current_span(span)
        log_event("my-event", {"key": "value"})
        assert len(span.events) == 1
        assert span.events[0].name == "my-event"
        assert span.events[0].attributes == {"key": "value"}

    def test_log_event_no_span_does_not_raise(self, client):
        set_current_span(None)
        log_event("my-event")  # should not raise

    def test_log_event_no_client_does_not_raise(self):
        _set_client(None)
        log_event("my-event")  # should not raise


class TestAttachMetadata:
    def test_attach_to_span(self, client):
        span = Span(name="test-span")
        set_current_span(span)
        attach_metadata("user_id", "u123")
        assert span.metadata["user_id"] == "u123"

    def test_attach_to_trace_when_no_span(self, client):
        trace = Trace(name="test-trace")
        set_current_trace(trace)
        set_current_span(None)
        attach_metadata("run_id", "r456")
        assert trace.metadata["run_id"] == "r456"

    def test_attach_no_context_does_not_raise(self, client):
        set_current_span(None)
        set_current_trace(None)
        attach_metadata("key", "value")  # should not raise

    def test_attach_no_client_does_not_raise(self):
        _set_client(None)
        attach_metadata("key", "value")  # should not raise


class TestLogLLMCall:
    def test_creates_llm_span(self, client):
        trace = Trace(name="test-trace")
        set_current_trace(trace)
        log_llm_call("gpt-4", input={"prompt": "hi"}, output={"text": "hello"})
        assert len(trace.spans) == 1
        assert trace.spans[0].kind == SpanKind.LLM
        assert "gpt-4" in trace.spans[0].name

    def test_no_client_does_not_raise(self):
        _set_client(None)
        log_llm_call("gpt-4")  # should not raise


class TestLogToolCall:
    def test_creates_tool_span(self, client):
        trace = Trace(name="test-trace")
        set_current_trace(trace)
        log_tool_call("search", input={"query": "hello"}, output={"results": []})
        assert len(trace.spans) == 1
        assert trace.spans[0].kind == SpanKind.TOOL
        assert "search" in trace.spans[0].name

    def test_no_client_does_not_raise(self):
        _set_client(None)
        log_tool_call("search")  # should not raise
