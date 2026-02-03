"""Tests for core SDK types: Span, Trace, Event."""

from __future__ import annotations

from datetime import datetime, timezone

from vigil._types import Event, Span, SpanKind, SpanStatus, Trace


class TestSpan:
    """Span model operations work correctly."""

    def test_defaults(self):
        span = Span(name="test")
        assert span.name == "test"
        assert span.kind == SpanKind.CUSTOM
        assert span.status == SpanStatus.UNSET
        assert span.end_time is None
        assert len(span.span_id) > 0

    def test_end(self):
        span = Span(name="test")
        assert span.end_time is None
        span.end(status=SpanStatus.OK)
        assert span.end_time is not None
        assert span.status == SpanStatus.OK

    def test_end_error(self):
        span = Span(name="test")
        span.end(status=SpanStatus.ERROR)
        assert span.status == SpanStatus.ERROR

    def test_add_event(self):
        span = Span(name="test")
        span.add_event("my-event", {"key": "value"})
        assert len(span.events) == 1
        assert span.events[0].name == "my-event"
        assert span.events[0].attributes == {"key": "value"}

    def test_set_input_output(self):
        span = Span(name="test")
        span.set_input({"prompt": "hello"})
        span.set_output({"response": "world"})
        assert span.input == {"prompt": "hello"}
        assert span.output == {"response": "world"}

    def test_serialization(self):
        span = Span(name="test", kind=SpanKind.LLM, trace_id="t1")
        data = span.model_dump(mode="json")
        assert data["name"] == "test"
        assert data["kind"] == "llm"
        assert data["trace_id"] == "t1"
        assert "span_id" in data

    def test_unique_ids(self):
        spans = [Span(name=f"span-{i}") for i in range(10)]
        ids = {s.span_id for s in spans}
        assert len(ids) == 10


class TestTrace:
    """Trace model operations work correctly."""

    def test_defaults(self):
        trace = Trace(name="test-trace")
        assert trace.name == "test-trace"
        assert len(trace.trace_id) > 0
        assert trace.end_time is None
        assert trace.spans == []

    def test_end(self):
        trace = Trace(name="test")
        trace.end()
        assert trace.end_time is not None

    def test_unique_ids(self):
        traces = [Trace(name=f"trace-{i}") for i in range(10)]
        ids = {t.trace_id for t in traces}
        assert len(ids) == 10


class TestEvent:
    """Event model works correctly."""

    def test_defaults(self):
        event = Event(name="test-event")
        assert event.name == "test-event"
        assert isinstance(event.timestamp, datetime)
        assert event.attributes == {}

    def test_with_attributes(self):
        event = Event(name="error", attributes={"code": 500})
        assert event.attributes == {"code": 500}
