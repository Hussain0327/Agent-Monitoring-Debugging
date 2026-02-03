"""Pydantic schemas for drift detection."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DriftAlertResponse(BaseModel):
    id: str
    project_id: str
    span_kind: str
    metric_name: str
    baseline_value: float
    current_value: float
    psi_score: float
    severity: str
    resolved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DriftSummary(BaseModel):
    total_alerts: int
    unresolved: int
    by_severity: dict[str, int]
    recent_alerts: list[DriftAlertResponse]
