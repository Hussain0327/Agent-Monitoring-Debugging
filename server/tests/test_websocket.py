"""Tests for WebSocket manager."""

from __future__ import annotations

import pytest

from vigil_server.services.websocket_manager import ConnectionManager


class FakeWebSocket:
    """Minimal WebSocket mock for testing."""

    def __init__(self):
        self.accepted = False
        self.messages: list[dict] = []
        self.closed = False

    async def accept(self):
        self.accepted = True

    async def send_json(self, data: dict):
        if self.closed:
            raise RuntimeError("WebSocket closed")
        self.messages.append(data)

    def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_connect_disconnect():
    mgr = ConnectionManager()
    ws = FakeWebSocket()
    await mgr.connect(ws, "proj-1")
    assert mgr.connection_count("proj-1") == 1

    mgr.disconnect(ws, "proj-1")
    assert mgr.connection_count("proj-1") == 0


@pytest.mark.asyncio
async def test_broadcast():
    mgr = ConnectionManager()
    ws1 = FakeWebSocket()
    ws2 = FakeWebSocket()
    await mgr.connect(ws1, "proj-1")
    await mgr.connect(ws2, "proj-1")

    await mgr.broadcast("proj-1", {"type": "test", "data": {}})
    assert len(ws1.messages) == 1
    assert len(ws2.messages) == 1
    assert ws1.messages[0]["type"] == "test"


@pytest.mark.asyncio
async def test_broadcast_different_projects():
    mgr = ConnectionManager()
    ws1 = FakeWebSocket()
    ws2 = FakeWebSocket()
    await mgr.connect(ws1, "proj-1")
    await mgr.connect(ws2, "proj-2")

    await mgr.broadcast("proj-1", {"type": "test", "data": {}})
    assert len(ws1.messages) == 1
    assert len(ws2.messages) == 0  # Different project


@pytest.mark.asyncio
async def test_broadcast_prunes_dead_connections():
    mgr = ConnectionManager()
    ws1 = FakeWebSocket()
    ws2 = FakeWebSocket()
    await mgr.connect(ws1, "proj-1")
    await mgr.connect(ws2, "proj-1")

    # Kill ws2
    ws2.closed = True

    await mgr.broadcast("proj-1", {"type": "test", "data": {}})
    assert mgr.connection_count("proj-1") == 1
    assert len(ws1.messages) == 1


@pytest.mark.asyncio
async def test_broadcast_no_connections():
    mgr = ConnectionManager()
    # Should not raise
    await mgr.broadcast("nonexistent", {"type": "test", "data": {}})


@pytest.mark.asyncio
async def test_connection_count_total():
    mgr = ConnectionManager()
    ws1 = FakeWebSocket()
    ws2 = FakeWebSocket()
    await mgr.connect(ws1, "proj-1")
    await mgr.connect(ws2, "proj-2")

    assert mgr.connection_count() == 2
    assert mgr.connection_count("proj-1") == 1
    assert mgr.connection_count("proj-2") == 1
