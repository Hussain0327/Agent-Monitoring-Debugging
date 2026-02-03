"""Drift detection endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from vigil_server.dependencies import CurrentProject, DBSession
from vigil_server.schemas.drift import DriftAlertResponse, DriftSummary
from vigil_server.services.drift_detector import get_drift_alerts, get_drift_summary

router = APIRouter(prefix="/drift", tags=["drift"])


@router.get("/alerts")
async def list_alerts(
    db: DBSession,
    project_id: CurrentProject,
    include_resolved: bool = False,
) -> list[DriftAlertResponse]:
    """List drift alerts for the current project."""
    alerts = await get_drift_alerts(db, project_id, include_resolved)
    return [DriftAlertResponse.model_validate(a) for a in alerts]


@router.get("/summary")
async def summary(
    db: DBSession,
    project_id: CurrentProject,
) -> DriftSummary:
    """Get drift alert summary for the current project."""
    data = await get_drift_summary(db, project_id)
    return DriftSummary(
        total_alerts=data["total_alerts"],
        unresolved=data["unresolved"],
        by_severity=data["by_severity"],
        recent_alerts=[DriftAlertResponse.model_validate(a) for a in data["recent_alerts"]],
    )
