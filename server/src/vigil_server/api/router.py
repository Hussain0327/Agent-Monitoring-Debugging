"""Root router that includes all sub-routers."""

from __future__ import annotations

from fastapi import APIRouter

from vigil_server.api.health import router as health_router
from vigil_server.api.v1.auth import router as auth_router
from vigil_server.api.v1.drift import router as drift_router
from vigil_server.api.v1.projects import router as projects_router
from vigil_server.api.v1.replay import router as replay_router
from vigil_server.api.v1.spans import router as spans_router
from vigil_server.api.v1.traces import router as traces_router

api_router = APIRouter()

# Health (no prefix)
api_router.include_router(health_router)

# V1 API
v1 = APIRouter(prefix="/v1")
v1.include_router(auth_router)
v1.include_router(traces_router)
v1.include_router(spans_router)
v1.include_router(projects_router)
v1.include_router(replay_router)
v1.include_router(drift_router)

api_router.include_router(v1)
