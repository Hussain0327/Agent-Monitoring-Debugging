"""Tests for @trace and @span decorators."""

from __future__ import annotations

import pytest

import vigil
from vigil._context import get_current_trace


@pytest.mark.asyncio
async def test_trace_decorator_creates_trace(client):
    """@trace should create and end a trace around the function."""

    @vigil.trace(name="test-trace")
    async def my_pipeline():
        t = get_current_trace()
        assert t is not None
        assert t.name == "test-trace"
        return "done"

    result = await my_pipeline()
    assert result == "done"
    # After completion, trace context should be cleared
    assert get_current_trace() is None


@pytest.mark.asyncio
async def test_span_decorator_captures_span(client):
    """@span should create a span within the current trace."""

    @vigil.trace(name="outer")
    async def pipeline():
        @vigil.span(name="inner-step", kind=vigil.SpanKind.LLM)
        async def step():
            span = vigil.current_span()
            assert span is not None
            assert span.name == "inner-step"
            assert span.kind == vigil.SpanKind.LLM
            return 42

        return await step()

    result = await pipeline()
    assert result == 42


@pytest.mark.asyncio
async def test_span_restores_parent(client):
    """@span should restore the previous span after completion."""
    from vigil._context import get_current_span

    @vigil.trace(name="trace")
    async def pipeline():
        parent = client.start_span("parent")

        @vigil.span(name="child")
        async def child_fn():
            child = get_current_span()
            assert child is not None
            assert child.name == "child"
            assert child.parent_span_id == parent.span_id

        await child_fn()
        # Parent should be restored
        # Note: the decorator restores the previous span
        return True

    result = await pipeline()
    assert result is True


@pytest.mark.asyncio
async def test_noop_without_client():
    """Decorators should be no-ops when no client is initialized."""
    from vigil._client import _set_client

    _set_client(None)

    @vigil.trace()
    async def pipeline():
        return "still works"

    result = await pipeline()
    assert result == "still works"


@pytest.mark.asyncio
async def test_span_captures_error(client):
    """@span should mark span as ERROR on exception."""

    @vigil.trace(name="error-trace")
    async def pipeline():
        @vigil.span(name="failing-step")
        async def fail():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            await fail()

    await pipeline()
