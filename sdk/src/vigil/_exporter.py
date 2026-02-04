"""Batched span exporter with async queue and HTTP flush.

Flushes every ``batch_size`` spans or ``flush_interval_ms``, whichever comes first.
Failed flushes are retried with exponential backoff capped at 30 s.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import queue
from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from vigil._config import SDKConfig
    from vigil._types import Span

logger = logging.getLogger("vigil.exporter")


class BatchSpanExporter:
    """Collects spans and flushes them in batches to the Vigil server.

    The exporter maintains an async queue for spans submitted from async
    code and a thread-safe :class:`queue.Queue` for spans submitted from
    synchronous contexts.  Both are drained during each flush cycle.
    """

    def __init__(self, config: SDKConfig) -> None:
        self._config = config
        self._queue: list[dict[str, Any]] = []
        self._sync_queue: queue.Queue[dict[str, Any]] = queue.Queue()
        self._client: httpx.AsyncClient | None = None
        self._flush_task: asyncio.Task[None] | None = None
        self._lock = asyncio.Lock()
        self._running = False
        self._consecutive_failures = 0

    # -- lifecycle -----------------------------------------------------------

    async def start(self) -> None:
        """Start the exporter and begin periodic flushing."""
        if self._running:
            return
        self._running = True
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self._config.timeout_seconds),
            headers=self._config.auth_headers,
        )
        self._flush_task = asyncio.create_task(self._periodic_flush())

    async def stop(self) -> None:
        """Stop periodic flushing, flush remaining spans, and close the HTTP client."""
        self._running = False
        if self._flush_task:
            self._flush_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._flush_task
        await self.flush()
        if self._client:
            await self._client.aclose()
            self._client = None

    # -- async interface -----------------------------------------------------

    async def export(self, span: Span) -> None:
        """Add a span to the async queue, flushing if the batch is full."""
        if not self._config.enabled:
            return
        async with self._lock:
            self._queue.append(span.model_dump(mode="json"))
            if len(self._queue) >= self._config.batch_size:
                await self._do_flush()

    async def flush(self) -> None:
        """Flush all queued spans (both async and sync) immediately."""
        async with self._lock:
            self._drain_sync_queue()
            await self._do_flush()

    # -- sync interface (thread-safe) ----------------------------------------

    def enqueue_sync(self, span: Span) -> None:
        """Thread-safe enqueue for synchronous callers.

        Spans are placed on a :class:`queue.Queue` and drained into the
        main queue on the next flush cycle.
        """
        if not self._config.enabled:
            return
        self._sync_queue.put_nowait(span.model_dump(mode="json"))

    # -- internals -----------------------------------------------------------

    def _drain_sync_queue(self) -> None:
        """Move all items from the thread-safe sync queue into the main queue.

        Must be called while ``self._lock`` is held.
        """
        while True:
            try:
                item = self._sync_queue.get_nowait()
                self._queue.append(item)
            except queue.Empty:
                break

    async def _do_flush(self) -> None:
        """Send all queued spans to the server.

        Must be called while ``self._lock`` is held — callers are
        responsible for acquiring the lock before calling this method.
        """
        if not self._queue or not self._client:
            return
        batch = self._queue[:]
        self._queue.clear()

        try:
            response = await self._client.post(
                self._config.ingest_url,
                json={"spans": batch},
            )
            response.raise_for_status()
            logger.debug("Flushed %d spans", len(batch))
            self._consecutive_failures = 0
        except httpx.HTTPError as exc:
            self._consecutive_failures += 1
            logger.warning("Failed to flush spans: %s", exc)
            # Re-add spans to front of queue for retry (no lock re-acquire)
            self._queue = batch + self._queue
            # Trim if queue is too large
            if len(self._queue) > self._config.max_queue_size:
                dropped = len(self._queue) - self._config.max_queue_size
                self._queue = self._queue[: self._config.max_queue_size]
                logger.warning("Dropped %d spans due to queue overflow", dropped)

    async def _periodic_flush(self) -> None:
        """Periodically flush spans with exponential backoff on failure."""
        base_interval = self._config.flush_interval_ms / 1000.0
        while self._running:
            # Exponential backoff: double interval on each consecutive failure, cap at 30s
            if self._consecutive_failures > 0:
                backoff = min(base_interval * (2**self._consecutive_failures), 30.0)
            else:
                backoff = base_interval
            await asyncio.sleep(backoff)
            try:
                await self.flush()
            except Exception:
                logger.exception("Error during periodic flush")
