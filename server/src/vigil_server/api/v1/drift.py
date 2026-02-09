"""Drift detection endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from vigil_server.dependencies import CurrentProject, DBSession, GuestProject  # noqa: TC001
from vigil_server.schemas.drift import DriftAlertResponse, DriftSummary
from vigil_server.services.drift_detector import (
    get_drift_alerts,
    get_drift_summary,
    resolve_drift_alert,
)
from vigil_server.services.websocket_manager import manager

router = APIRouter(prefix="/drift", tags=["drift"])


@router.get("/alerts")
async def list_alerts(
    db: DBSession,
    project_id: GuestProject,
    include_resolved: bool = False,
) -> list[DriftAlertResponse]:
    """List drift alerts for the current project."""
    alerts = await get_drift_alerts(db, project_id, include_resolved)
    return [DriftAlertResponse.model_validate(a) for a in alerts]


@router.get("/summary")
async def summary(
    db: DBSession,
    project_id: GuestProject,
) -> DriftSummary:
    """Get drift alert summary for the current project."""
    data = await get_drift_summary(db, project_id)
    return DriftSummary(
        total_alerts=data["total_alerts"],
        unresolved=data["unresolved"],
        by_severity=data["by_severity"],
        recent_alerts=[DriftAlertResponse.model_validate(a) for a in data["recent_alerts"]],
    )


@router.patch("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    db: DBSession,
    project_id: CurrentProject,
) -> DriftAlertResponse:
    """Resolve a drift alert."""
    alert = await resolve_drift_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Drift alert not found")

    # Broadcast resolution
    await manager.broadcast(
        project_id,
        {
            "type": "drift.resolved",
            "data": {"alert_id": alert_id},
        },
    )

    return DriftAlertResponse.model_validate(alert)
