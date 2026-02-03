"""Tests for BatchSpanExporter batching and flush logic."""

from __future__ import annotations

import pytest
import respx

from vigil._config import SDKConfig
from vigil._exporter import BatchSpanExporter
from vigil._types import Span


@pytest.fixture
def exporter_config():
    return SDKConfig(
        endpoint="http://test-server:8000",
        api_key="test-key",
        batch_size=3,
        flush_interval_ms=50,
    )


@pytest.mark.asyncio
async def test_flush_on_batch_size(exporter_config):
    """Exporter should flush when batch_size is reached."""
    with respx.mock(assert_all_called=False) as mock:
        route = mock.post("http://test-server:8000/v1/traces").respond(200, json={"ok": True})

        exporter = BatchSpanExporter(exporter_config)
        await exporter.start()

        # Export batch_size spans to trigger auto-flush
        for i in range(3):
            await exporter.export(Span(name=f"span-{i}"))

        # Should have flushed once (3 spans = batch_size)
        assert route.call_count == 1

        await exporter.stop()


@pytest.mark.asyncio
async def test_flush_on_stop(exporter_config):
    """Exporter should flush remaining spans on stop."""
    with respx.mock(assert_all_called=False) as mock:
        route = mock.post("http://test-server:8000/v1/traces").respond(200, json={"ok": True})

        exporter = BatchSpanExporter(exporter_config)
        await exporter.start()

        # Export fewer than batch_size
        await exporter.export(Span(name="span-1"))
        assert route.call_count == 0

        # Stop should flush the remaining span
        await exporter.stop()
        assert route.call_count == 1


@pytest.mark.asyncio
async def test_noop_when_disabled():
    """Exporter should not export when disabled."""
    config = SDKConfig(enabled=False)
    with respx.mock(assert_all_called=False) as mock:
        route = mock.post("http://localhost:8000/v1/traces").respond(200, json={"ok": True})

        exporter = BatchSpanExporter(config)
        await exporter.start()
        await exporter.export(Span(name="should-not-send"))
        await exporter.flush()
        await exporter.stop()

        assert route.call_count == 0


@pytest.mark.asyncio
async def test_manual_flush(exporter_config):
    """Manual flush should send all queued spans."""
    with respx.mock(assert_all_called=False) as mock:
        route = mock.post("http://test-server:8000/v1/traces").respond(200, json={"ok": True})

        exporter = BatchSpanExporter(exporter_config)
        await exporter.start()

        await exporter.export(Span(name="span-1"))
        await exporter.export(Span(name="span-2"))
        assert route.call_count == 0

        await exporter.flush()
        assert route.call_count == 1

        await exporter.stop()
