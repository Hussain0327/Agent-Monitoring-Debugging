"""Tests for notification endpoints."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from vigil_server.main import app
from vigil_server.models.notification import Notification


@pytest.mark.asyncio
async def test_list_empty(client: AsyncClient):
    """No notifications returns empty list."""
    resp = await client.get("/v1/notifications")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_and_list(client: AsyncClient, db_session):
    """Creating notifications and listing them."""
    n1 = Notification(
        project_id="test-project",
        type="drift_alert",
        title="Drift detected",
        body="PSI=0.3 on llm spans",
        reference_id="alert-1",
    )
    n2 = Notification(
        project_id="test-project",
        type="replay_complete",
        title="Replay done",
        body="Replay xyz completed",
    )
    db_session.add_all([n1, n2])
    await db_session.flush()

    resp = await client.get("/v1/notifications")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_unread_only_filter(client: AsyncClient, db_session):
    """Filter for unread notifications only."""
    n1 = Notification(
        project_id="test-project", type="drift_alert", title="Unread alert"
    )
    n2 = Notification(
        project_id="test-project", type="drift_alert", title="Read alert", read=True
    )
    db_session.add_all([n1, n2])
    await db_session.flush()

    resp = await client.get("/v1/notifications?unread_only=true")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "Unread alert"


@pytest.mark.asyncio
async def test_mark_read(client: AsyncClient, db_session):
    """Mark a notification as read."""
    n = Notification(
        project_id="test-project", type="drift_alert", title="To be read"
    )
    db_session.add(n)
    await db_session.flush()

    resp = await client.patch(f"/v1/notifications/{n.id}/read")
    assert resp.status_code == 200
    assert resp.json()["read"] is True


@pytest.mark.asyncio
async def test_mark_read_not_found(client: AsyncClient):
    """Mark non-existent notification returns 404."""
    resp = await client.patch("/v1/notifications/nonexistent/read")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_mark_all_read(client: AsyncClient, db_session):
    """Mark all notifications as read."""
    for i in range(3):
        db_session.add(
            Notification(
                project_id="test-project", type="drift_alert", title=f"Alert {i}"
            )
        )
    await db_session.flush()

    resp = await client.post("/v1/notifications/read-all")
    assert resp.status_code == 200
    assert resp.json()["marked_read"] == 3


@pytest.mark.asyncio
async def test_unread_count(client: AsyncClient, db_session):
    """Get unread count."""
    db_session.add(
        Notification(
            project_id="test-project", type="drift_alert", title="Unread"
        )
    )
    db_session.add(
        Notification(
            project_id="test-project", type="drift_alert", title="Read", read=True
        )
    )
    await db_session.flush()

    resp = await client.get("/v1/notifications/count")
    assert resp.status_code == 200
    assert resp.json()["unread"] == 1
