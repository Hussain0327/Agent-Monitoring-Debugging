"""Tests for ContextVar trace/span propagation."""

from __future__ import annotations

import asyncio

from vigil._context import (
    get_current_span,
    get_current_trace,
    set_current_span,
    set_current_trace,
)
from vigil._types import Span, Trace


class TestTraceContext:
    """Trace context get/set works correctly."""

    def test_default_is_none(self):
        set_current_trace(None)
        assert get_current_trace() is None

    def test_set_and_get(self):
        trace = Trace(name="test")
        set_current_trace(trace)
        assert get_current_trace() is trace
        set_current_trace(None)

    def test_clear(self):
        trace = Trace(name="test")
        set_current_trace(trace)
        set_current_trace(None)
        assert get_current_trace() is None


class TestSpanContext:
    """Span context get/set works correctly."""

    def test_default_is_none(self):
        set_current_span(None)
        assert get_current_span() is None

    def test_set_and_get(self):
        span = Span(name="test-span", trace_id="t1")
        set_current_span(span)
        assert get_current_span() is span
        set_current_span(None)

    def test_clear(self):
        span = Span(name="test-span", trace_id="t1")
        set_current_span(span)
        set_current_span(None)
        assert get_current_span() is None


class TestContextIsolation:
    """Context is isolated across async tasks."""

    async def test_async_task_isolation(self):
        results = {}

        async def task_a():
            trace = Trace(name="task-a")
            set_current_trace(trace)
            await asyncio.sleep(0.01)
            results["a"] = get_current_trace()
            set_current_trace(None)

        async def task_b():
            trace = Trace(name="task-b")
            set_current_trace(trace)
            await asyncio.sleep(0.01)
            results["b"] = get_current_trace()
            set_current_trace(None)

        await asyncio.gather(task_a(), task_b())

        assert results["a"] is not None
        assert results["b"] is not None
        assert results["a"].name == "task-a"
        assert results["b"].name == "task-b"
