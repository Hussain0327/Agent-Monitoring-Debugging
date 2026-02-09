"""Trace replay endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from vigil_server.dependencies import CurrentProject, DBSession, GuestProject  # noqa: TC001
from vigil_server.schemas.replay import (
    ReplayDiffResponse,
    ReplayEstimateResponse,
    ReplayRequest,
    ReplayRunResponse,
)
from vigil_server.services.encryption import decrypt
from vigil_server.services.replay_engine import (
    cancel_replay,
    confirm_replay,
    create_replay_estimate,
    get_replay_diff,
    get_replay_run,
)

router = APIRouter(prefix="/traces", tags=["replay"])


@router.post("/{trace_id}/replay")
async def replay(
    trace_id: str,
    body: ReplayRequest,
    db: DBSession,
    project_id: CurrentProject,
) -> ReplayEstimateResponse:
    """Create a replay cost estimate (two-phase: estimate then confirm)."""
    try:
        result = await create_replay_estimate(db, trace_id, body.mutations, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ReplayEstimateResponse(**result)


@router.post("/{trace_id}/replay/{replay_id}/confirm")
async def confirm(
    trace_id: str,
    replay_id: str,
    db: DBSession,
    project_id: CurrentProject,
) -> ReplayRunResponse:
    """Confirm a replay estimate and start execution."""
    run = await get_replay_run(db, replay_id)
    if not run or run.original_trace_id != trace_id:
        raise HTTPException(status_code=404, detail="Replay run not found")

    # Build API key resolver from project settings
    async def get_api_key(provider: str) -> str | None:
        from sqlalchemy import select

        from vigil_server.db.session import async_session
        from vigil_server.models.project_settings import ProjectSettings

        async with async_session() as session:
            stmt = select(ProjectSettings).where(ProjectSettings.project_id == project_id)
            result = await session.execute(stmt)
            settings = result.scalar_one_or_none()
            if not settings:
                return None
            if provider == "openai" and settings.openai_api_key_encrypted:
                return decrypt(settings.openai_api_key_encrypted)
            if provider == "anthropic" and settings.anthropic_api_key_encrypted:
                return decrypt(settings.anthropic_api_key_encrypted)
            return None

    try:
        confirmed_run = await confirm_replay(db, replay_id, get_api_key=get_api_key)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ReplayRunResponse.model_validate(confirmed_run)


@router.post("/{trace_id}/replay/{replay_id}/cancel")
async def cancel(
    trace_id: str,
    replay_id: str,
    db: DBSession,
    _auth: CurrentProject,
) -> ReplayRunResponse:
    """Cancel a pending replay."""
    run = await get_replay_run(db, replay_id)
    if not run or run.original_trace_id != trace_id:
        raise HTTPException(status_code=404, detail="Replay run not found")
    try:
        cancelled = await cancel_replay(db, replay_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ReplayRunResponse.model_validate(cancelled)


@router.get("/{trace_id}/replay/{replay_id}")
async def get_replay_status(
    trace_id: str,
    replay_id: str,
    db: DBSession,
    _auth: GuestProject,
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
    _auth: GuestProject,
) -> ReplayDiffResponse:
    """Get the diff output from a completed replay run."""
    diff = await get_replay_diff(db, trace_id, replay_id)
    if not diff:
        raise HTTPException(status_code=404, detail="Replay run not found")
    return diff
