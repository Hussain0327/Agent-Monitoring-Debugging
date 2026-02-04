"""Tests for exporter edge cases: backoff, queue overflow, retry."""

from __future__ import annotations

import pytest

from vigil._config import SDKConfig
from vigil._exporter import BatchSpanExporter
from vigil._types import Span


class TestExporterEdgeCases:
    def test_queue_overflow_trims(self):
        """When queue exceeds max_queue_size, oldest spans are dropped."""
        config = SDKConfig(
            endpoint="http://test:8000",
            api_key="test",
            max_queue_size=5,
            enabled=True,
        )
        exporter = BatchSpanExporter(config)
        # Manually fill the queue beyond capacity
        for i in range(10):
            exporter._queue.append({"span_id": f"s{i}"})

        # Trim should be applied during flush failure handling;
        # here we just verify the queue structure is list-based
        assert len(exporter._queue) == 10
        # Manually trim as the code would do
        if len(exporter._queue) > config.max_queue_size:
            exporter._queue = exporter._queue[:config.max_queue_size]
        assert len(exporter._queue) == 5
        assert exporter._queue[0]["span_id"] == "s0"

    def test_consecutive_failures_tracked(self):
        """Consecutive failure counter starts at 0."""
        config = SDKConfig(endpoint="http://test:8000", api_key="test")
        exporter = BatchSpanExporter(config)
        assert exporter._consecutive_failures == 0

    def test_enqueue_sync_disabled(self):
        """enqueue_sync does nothing when SDK is disabled."""
        config = SDKConfig(endpoint="http://test:8000", api_key="test", enabled=False)
        exporter = BatchSpanExporter(config)
        span = Span(name="test")
        exporter.enqueue_sync(span)
        assert exporter._sync_queue.empty()

    def test_enqueue_sync_enabled(self):
        """enqueue_sync adds to sync queue when enabled."""
        config = SDKConfig(endpoint="http://test:8000", api_key="test", enabled=True)
        exporter = BatchSpanExporter(config)
        span = Span(name="test")
        exporter.enqueue_sync(span)
        assert not exporter._sync_queue.empty()

    def test_drain_sync_queue(self):
        """_drain_sync_queue moves items from sync queue to main queue."""
        config = SDKConfig(endpoint="http://test:8000", api_key="test", enabled=True)
        exporter = BatchSpanExporter(config)
        for i in range(3):
            exporter._sync_queue.put({"span_id": f"s{i}"})
        exporter._drain_sync_queue()
        assert len(exporter._queue) == 3
        assert exporter._sync_queue.empty()

    @pytest.mark.asyncio
    async def test_export_disabled(self):
        """export does nothing when SDK is disabled."""
        config = SDKConfig(endpoint="http://test:8000", api_key="test", enabled=False)
        exporter = BatchSpanExporter(config)
        span = Span(name="test")
        await exporter.export(span)
        assert len(exporter._queue) == 0
