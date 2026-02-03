"""Trace replay endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from vigil_server.dependencies import DBSession
from vigil_server.services.replay_engine import replay_trace

router = APIRouter(prefix="/traces", tags=["replay"])


class ReplayRequest(BaseModel):
    mutations: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Map of span_id -> {field: new_value} for input overrides",
    )


@router.post("/{trace_id}/replay")
async def replay(
    trace_id: str,
    body: ReplayRequest,
    db: DBSession,
) -> dict[str, Any]:
    """Replay a trace with optional input mutations."""
    try:
        result = await replay_trace(db, trace_id, body.mutations)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return result.to_dict()
