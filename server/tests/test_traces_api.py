"""Tests for trace query endpoints."""

from __future__ import annotations

import uuid

import pytest


@pytest.mark.asyncio
async def test_list_traces_empty(client):
    """GET /v1/traces should return empty list when no traces exist."""
    response = await client.get("/v1/traces")
    assert response.status_code == 200
    data = response.json()
    assert data["traces"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_get_trace_not_found(client):
    """GET /v1/traces/{id} should return 404 for nonexistent trace."""
    response = await client.get("/v1/traces/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_ingest_then_list(client):
    """Traces should be listable after ingestion."""
    # Ingest
    ingest_resp = await client.post(
        "/v1/traces",
        json={
            "spans": [{"span_id": "s1", "name": "test-span", "kind": "chain"}],
            "trace_name": "my-trace",
        },
    )
    assert ingest_resp.status_code == 201
    trace_id = ingest_resp.json()["trace_id"]

    # List
    list_resp = await client.get("/v1/traces")
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert data["total"] == 1
    assert data["traces"][0]["id"] == trace_id

    # Get single
    get_resp = await client.get(f"/v1/traces/{trace_id}")
    assert get_resp.status_code == 200
    trace_data = get_resp.json()
    assert trace_data["name"] == "my-trace"
    assert len(trace_data["spans"]) == 1


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """GET /health should return ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_patch_trace(client):
    """PATCH /v1/traces/{id} should update status and metadata."""
    span_id = uuid.uuid4().hex
    trace_id = uuid.uuid4().hex
    await client.post(
        "/v1/traces",
        json={
            "spans": [{"span_id": span_id, "trace_id": trace_id, "name": "s", "kind": "custom"}],
            "trace_name": "patch-test",
        },
    )

    res = await client.patch(
        f"/v1/traces/{trace_id}",
        json={"status": "ok", "metadata": {"env": "test"}},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["metadata"]["env"] == "test"


@pytest.mark.asyncio
async def test_patch_trace_not_found(client):
    """PATCH /v1/traces/{id} with nonexistent trace should return 404."""
    res = await client.patch(
        "/v1/traces/nonexistent",
        json={"status": "ok"},
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_append_event(client):
    """POST /v1/traces/{id}/events/{span_id} should append an event."""
    span_id = uuid.uuid4().hex
    trace_id = uuid.uuid4().hex
    await client.post(
        "/v1/traces",
        json={
            "spans": [{"span_id": span_id, "trace_id": trace_id, "name": "s", "kind": "custom"}],
            "trace_name": "event-test",
        },
    )

    res = await client.post(
        f"/v1/traces/{trace_id}/events/{span_id}",
        json={"name": "test-event", "attributes": {"key": "value"}},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "test-event"
    assert data["attributes"]["key"] == "value"


@pytest.mark.asyncio
async def test_append_event_span_not_found(client):
    """POST /v1/traces/{id}/events/{span_id} with bad span_id returns 404."""
    span_id = uuid.uuid4().hex
    trace_id = uuid.uuid4().hex
    await client.post(
        "/v1/traces",
        json={
            "spans": [{"span_id": span_id, "trace_id": trace_id, "name": "s", "kind": "custom"}],
            "trace_name": "event-test",
        },
    )

    res = await client.post(
        f"/v1/traces/{trace_id}/events/nonexistent-span",
        json={"name": "test-event"},
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_list_traces_with_status_filter(client):
    """GET /v1/traces?status=ok should filter by status."""
    t1 = uuid.uuid4().hex
    t2 = uuid.uuid4().hex
    await client.post(
        "/v1/traces",
        json={
            "spans": [{"span_id": uuid.uuid4().hex, "trace_id": t1, "name": "s", "kind": "custom"}],
            "trace_name": "trace-1",
        },
    )
    await client.post(
        "/v1/traces",
        json={
            "spans": [{"span_id": uuid.uuid4().hex, "trace_id": t2, "name": "s", "kind": "custom"}],
            "trace_name": "trace-2",
        },
    )
    # Update one trace to "ok"
    await client.patch(f"/v1/traces/{t1}", json={"status": "ok"})

    res = await client.get("/v1/traces?status=ok")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["traces"][0]["id"] == t1


@pytest.mark.asyncio
async def test_ingest_with_external_id(client):
    """POST /v1/traces should store external_id."""
    res = await client.post(
        "/v1/traces",
        json={
            "spans": [{"span_id": uuid.uuid4().hex, "name": "s", "kind": "custom"}],
            "trace_name": "ext-trace",
            "external_id": "ext-123",
        },
    )
    assert res.status_code == 201
    trace_id = res.json()["trace_id"]
    get_res = await client.get(f"/v1/traces/{trace_id}")
    assert get_res.json()["external_id"] == "ext-123"
