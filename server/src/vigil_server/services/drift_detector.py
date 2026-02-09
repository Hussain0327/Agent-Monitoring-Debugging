"""Drift detection service using Population Stability Index (PSI)."""

from __future__ import annotations

import logging
import math
from collections import defaultdict
from datetime import UTC
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from vigil_server.exceptions import VigilError
from vigil_server.models.drift import DriftAlert

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession
from vigil_server.models.span import Span as SpanModel

logger = logging.getLogger("vigil_server.services.drift")

# PSI thresholds
PSI_LOW = 0.1
PSI_MEDIUM = 0.2


def compute_psi(baseline: list[float], current: list[float], bins: int = 10) -> float:
    """Compute Population Stability Index between two distributions.

    PSI < 0.1: no significant change
    PSI 0.1-0.2: moderate change
    PSI > 0.2: significant change

    Returns 0.0 when inputs are empty or have zero variance.
    """
    if not baseline or not current:
        return 0.0

    all_values = baseline + current
    min_val = min(all_values)
    max_val = max(all_values)

    if min_val == max_val:
        return 0.0

    bin_width = (max_val - min_val) / bins
    eps = 1e-4

    def histogram(values: list[float]) -> list[float]:
        counts = [0] * bins
        for v in values:
            idx = min(int((v - min_val) / bin_width), bins - 1)
            counts[idx] += 1
        total = len(values)
        return [(c / total) + eps for c in counts]

    baseline_pct = histogram(baseline)
    current_pct = histogram(current)

    psi = 0.0
    for b, c in zip(baseline_pct, current_pct, strict=True):
        psi += (c - b) * math.log(c / b)

    return psi


def severity_from_psi(psi: float) -> str:
    """Return a severity label for a given PSI score."""
    if psi < PSI_LOW:
        return "low"
    elif psi < PSI_MEDIUM:
        return "medium"
    return "high"


async def detect_drift(
    session: AsyncSession,
    project_id: str,
    baseline_window_hours: int = 24,
    current_window_hours: int = 1,
) -> list[DriftAlert]:
    """Compare recent span latencies against baseline to detect drift.

    Groups spans by kind and compares latency distributions.
    """
    from datetime import datetime, timedelta

    now = datetime.now(UTC)
    baseline_start = now - timedelta(hours=baseline_window_hours)
    current_start = now - timedelta(hours=current_window_hours)

    try:
        # Query spans grouped by kind for baseline and current windows
        stmt = (
            select(SpanModel.kind, SpanModel.start_time, SpanModel.end_time)
            .where(SpanModel.start_time >= baseline_start)
            .join(SpanModel.trace)
        )

        result = await session.execute(stmt)
        rows = result.all()
    except SQLAlchemyError as exc:
        logger.exception("Database error querying spans for drift detection")
        raise VigilError("Failed to query spans for drift detection", status_code=500) from exc

    # Group latencies by kind and window
    baseline_latencies: dict[str, list[float]] = defaultdict(list)
    current_latencies: dict[str, list[float]] = defaultdict(list)

    for kind, start, end in rows:
        if not start or not end:
            continue
        latency = (end - start).total_seconds()
        if latency < 0:
            continue  # Skip invalid spans where end < start
        if start >= current_start:
            current_latencies[kind].append(latency)
        baseline_latencies[kind].append(latency)

    # Compute PSI for each span kind
    alerts: list[DriftAlert] = []
    for kind in baseline_latencies:
        baseline = baseline_latencies[kind]
        current = current_latencies.get(kind, [])
        if len(baseline) < 10 or len(current) < 5:
            continue

        psi = compute_psi(baseline, current)
        sev = severity_from_psi(psi)

        if psi >= PSI_LOW:
            baseline_mean = sum(baseline) / len(baseline)
            current_mean = sum(current) / len(current) if current else 0.0

            alert = DriftAlert(
                project_id=project_id,
                span_kind=kind,
                metric_name="latency",
                baseline_value=baseline_mean,
                current_value=current_mean,
                psi_score=psi,
                severity=sev,
            )
            session.add(alert)
            alerts.append(alert)

    try:
        await session.flush()
    except SQLAlchemyError as exc:
        logger.exception("Database error saving drift alerts")
        raise VigilError("Failed to save drift alerts", status_code=500) from exc

    logger.debug("Drift detection found %d alerts for project %s", len(alerts), project_id)
    return alerts


async def resolve_drift_alert(
    session: AsyncSession,
    alert_id: str,
) -> DriftAlert | None:
    """Mark a drift alert as resolved."""
    alert = await session.get(DriftAlert, alert_id)
    if alert:
        alert.resolved = True
        await session.flush()
    return alert


async def get_drift_alerts(
    session: AsyncSession,
    project_id: str,
    include_resolved: bool = False,
) -> Sequence[DriftAlert]:
    """Fetch drift alerts for a project."""
    try:
        stmt = (
            select(DriftAlert)
            .where(DriftAlert.project_id == project_id)
            .order_by(DriftAlert.created_at.desc())
        )
        if not include_resolved:
            stmt = stmt.where(DriftAlert.resolved == False)  # noqa: E712

        result = await session.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception("Database error fetching drift alerts")
        raise VigilError("Failed to fetch drift alerts", status_code=500) from exc


async def get_drift_summary(
    session: AsyncSession,
    project_id: str,
) -> dict:
    """Get a summary of drift alerts."""
    all_alerts = await get_drift_alerts(session, project_id, include_resolved=True)
    unresolved = [a for a in all_alerts if not a.resolved]

    by_severity: dict[str, int] = defaultdict(int)
    for a in unresolved:
        by_severity[a.severity] += 1

    return {
        "total_alerts": len(all_alerts),
        "unresolved": len(unresolved),
        "by_severity": dict(by_severity),
        "recent_alerts": list(all_alerts[:10]),
    }
