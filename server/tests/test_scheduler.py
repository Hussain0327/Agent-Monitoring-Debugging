"""Tests for drift scheduler."""

from __future__ import annotations

import pytest

from vigil_server.services.scheduler import DriftScheduler


@pytest.mark.asyncio
async def test_scheduler_start_stop():
    """Scheduler starts and stops cleanly."""
    scheduler = DriftScheduler()
    await scheduler.start()
    assert scheduler._running is True
    assert scheduler._task is not None

    await scheduler.stop()
    assert scheduler._running is False
    assert scheduler._task is None


@pytest.mark.asyncio
async def test_scheduler_double_start():
    """Starting an already-running scheduler is a no-op."""
    scheduler = DriftScheduler()
    await scheduler.start()
    task1 = scheduler._task
    await scheduler.start()
    task2 = scheduler._task
    assert task1 is task2
    await scheduler.stop()


@pytest.mark.asyncio
async def test_scheduler_stop_when_not_started():
    """Stopping a not-started scheduler is safe."""
    scheduler = DriftScheduler()
    await scheduler.stop()  # Should not raise
