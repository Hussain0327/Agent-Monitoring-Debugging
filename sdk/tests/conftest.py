"""Shared fixtures for SDK tests."""

from __future__ import annotations

import pytest
import respx

from vigil._client import VigilClient, _set_client
from vigil._config import SDKConfig
from vigil._context import set_current_span, set_current_trace


@pytest.fixture
def mock_server():
    """Mock Vigil server that accepts span ingestion."""
    with respx.mock(assert_all_called=False) as mock:
        mock.post("http://test-server:8000/v1/traces").respond(200, json={"ok": True})
        yield mock


@pytest.fixture
def config():
    return SDKConfig(
        endpoint="http://test-server:8000",
        api_key="test-key",
        project_id="test-project",
        batch_size=10,
        flush_interval_ms=100,
    )


@pytest.fixture
async def client(config, mock_server):
    """Initialized VigilClient with mocked server."""
    c = VigilClient(config)
    await c.start()
    _set_client(c)
    yield c
    await c.shutdown()
    _set_client(None)
    set_current_trace(None)
    set_current_span(None)
