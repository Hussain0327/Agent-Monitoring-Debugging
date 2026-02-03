"""Tests for project CRUD and API key rotation."""

from __future__ import annotations

import pytest


class TestProjectCreate:
    async def test_create_project(self, client):
        res = await client.post("/v1/projects", json={"name": "Test Project"})
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "Test Project"
        assert len(data["api_keys"]) >= 1
        assert data["api_keys"][0]["key"].startswith("vgl_")

    async def test_create_project_with_description(self, client):
        res = await client.post(
            "/v1/projects",
            json={"name": "My Project", "description": "A test project"},
        )
        assert res.status_code == 201
        assert res.json()["description"] == "A test project"

    async def test_create_project_empty_name_rejected(self, client):
        res = await client.post("/v1/projects", json={"name": ""})
        assert res.status_code == 422


class TestProjectList:
    async def test_list_empty(self, client):
        res = await client.get("/v1/projects")
        assert res.status_code == 200
        data = res.json()
        assert data["projects"] == []
        assert data["total"] == 0

    async def test_list_after_create(self, client):
        await client.post("/v1/projects", json={"name": "P1"})
        await client.post("/v1/projects", json={"name": "P2"})
        res = await client.get("/v1/projects")
        assert res.status_code == 200
        assert res.json()["total"] == 2


class TestProjectGet:
    async def test_get_not_found(self, client):
        res = await client.get("/v1/projects/nonexistent")
        assert res.status_code == 404

    async def test_get_existing(self, client):
        create_res = await client.post("/v1/projects", json={"name": "Findme"})
        project_id = create_res.json()["id"]
        res = await client.get(f"/v1/projects/{project_id}")
        assert res.status_code == 200
        assert res.json()["name"] == "Findme"


class TestKeyRotation:
    async def test_rotate_key(self, client):
        create_res = await client.post("/v1/projects", json={"name": "Rotatable"})
        project_id = create_res.json()["id"]
        rotate_res = await client.post(f"/v1/projects/{project_id}/rotate-key")
        assert rotate_res.status_code == 201
        data = rotate_res.json()
        assert "key" in data
        assert data["key"].startswith("vgl_")
