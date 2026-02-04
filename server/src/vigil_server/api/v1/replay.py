"""Trace replay endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from vigil_server.dependencies import CurrentProject, DBSession  # noqa: TC001
from vigil_server.schemas.replay import ReplayDiffResponse, ReplayRequest, ReplayRunResponse
from vigil_server.services.replay_engine import get_replay_diff, get_replay_run, replay_trace

router = APIRouter(prefix="/traces", tags=["replay"])


@router.post("/{trace_id}/replay")
async def replay(
    trace_id: str,
    body: ReplayRequest,
    db: DBSession,
    _auth: CurrentProject,
) -> dict[str, Any]:
    """Replay a trace with optional input mutations, persisting the run."""
    try:
        result = await replay_trace(db, trace_id, body.mutations)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return result.to_dict()


@router.get("/{trace_id}/replay/{replay_id}")
async def get_replay_status(
    trace_id: str,
    replay_id: str,
    db: DBSession,
    _auth: CurrentProject,
) -> ReplayRunResponse:
    """Get the status of a replay run."""
    run = await get_replay_run(db, replay_id)
    if not run or run.original_trace_id != trace_id:
        raise HTTPException(status_code=404, detail="Replay run not found")
    return ReplayRunResponse.model_validate(run)


@router.get("/{trace_id}/replay/{replay_id}/diff")
async def get_replay_diff_endpoint(
    trace_id: str,
    replay_id: str,
    db: DBSession,
    _auth: CurrentProject,
) -> ReplayDiffResponse:
    """Get the diff output from a completed replay run."""
    diff = await get_replay_diff(db, trace_id, replay_id)
    if not diff:
        raise HTTPException(status_code=404, detail="Replay run not found")
    return diff
