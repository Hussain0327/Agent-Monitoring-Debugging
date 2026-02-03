"""Tests for trace query endpoints."""

from __future__ import annotations

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
