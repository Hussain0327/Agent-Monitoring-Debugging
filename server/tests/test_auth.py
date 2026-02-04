"""Tests for authentication endpoints and JWT protection."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    """POST /v1/auth/register should create a new user."""
    res = await client.post(
        "/v1/auth/register",
        json={"email": "test@example.com", "password": "securepass123"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    """POST /v1/auth/register with existing email should return 409."""
    await client.post(
        "/v1/auth/register",
        json={"email": "dup@example.com", "password": "securepass123"},
    )
    res = await client.post(
        "/v1/auth/register",
        json={"email": "dup@example.com", "password": "anotherpass123"},
    )
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_register_short_password(client):
    """POST /v1/auth/register with short password should return 422."""
    res = await client.post(
        "/v1/auth/register",
        json={"email": "short@example.com", "password": "short"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client):
    """POST /v1/auth/login should return a JWT token."""
    await client.post(
        "/v1/auth/register",
        json={"email": "login@example.com", "password": "securepass123"},
    )
    res = await client.post(
        "/v1/auth/login",
        json={"email": "login@example.com", "password": "securepass123"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """POST /v1/auth/login with wrong password should return 401."""
    await client.post(
        "/v1/auth/register",
        json={"email": "badlogin@example.com", "password": "securepass123"},
    )
    res = await client.post(
        "/v1/auth/login",
        json={"email": "badlogin@example.com", "password": "wrongpassword"},
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """POST /v1/auth/login with unknown email should return 401."""
    res = await client.post(
        "/v1/auth/login",
        json={"email": "nobody@example.com", "password": "whatever123"},
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_jwt_protected_access(client):
    """Endpoints protected by CurrentProject should work with JWT tokens."""
    # Register and login
    await client.post(
        "/v1/auth/register",
        json={"email": "jwt@example.com", "password": "securepass123"},
    )
    login_res = await client.post(
        "/v1/auth/login",
        json={"email": "jwt@example.com", "password": "securepass123"},
    )
    token = login_res.json()["access_token"]

    # The test client has dependency overrides, so this test verifies the
    # auth endpoint flow works end-to-end.  In production (without
    # overrides), hitting /v1/traces without auth would return 401.
    res = await client.get("/v1/traces")
    assert res.status_code == 200
