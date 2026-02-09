"""Background drift detection scheduler."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from datetime import UTC, datetime

logger = logging.getLogger("vigil_server.services.scheduler")


class DriftScheduler:
    """Periodically checks for drift on projects with detection enabled."""

    def __init__(self) -> None:
        self._task: asyncio.Task | None = None
        self._running = False
        # Track last check time per project
        self._last_check: dict[str, datetime] = {}

    async def start(self) -> None:
        """Start the scheduler loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Drift scheduler started")

    async def stop(self) -> None:
        """Stop the scheduler loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None
        logger.info("Drift scheduler stopped")

    async def _loop(self) -> None:
        """Main scheduler loop — checks every 30 seconds for due projects."""
        while self._running:
            try:
                await self._check_projects()
            except Exception:
                logger.exception("Error in drift scheduler loop")
            await asyncio.sleep(30)

    async def _check_projects(self) -> None:
        """Check all projects with drift detection enabled."""
        from sqlalchemy import select

        from vigil_server.db.session import async_session
        from vigil_server.models.project_settings import ProjectSettings
        from vigil_server.services.drift_detector import detect_drift
        from vigil_server.services.notification_service import create_notification
        from vigil_server.services.websocket_manager import manager

        async with async_session() as session, session.begin():
            stmt = select(ProjectSettings).where(
                ProjectSettings.drift_check_enabled == True  # noqa: E712
            )
            result = await session.execute(stmt)
            settings_list = result.scalars().all()

        now = datetime.now(UTC)

        for ps in settings_list:
            last = self._last_check.get(ps.project_id)
            interval_seconds = ps.drift_check_interval_minutes * 60

            if last and (now - last).total_seconds() < interval_seconds:
                continue

            # Time to check this project
            logger.debug("Running drift check for project %s", ps.project_id)
            self._last_check[ps.project_id] = now

            try:
                async with async_session() as session, session.begin():
                    alerts = await detect_drift(session, ps.project_id)

                    for alert in alerts:
                        await create_notification(
                            session,
                            project_id=ps.project_id,
                            type="drift_alert",
                            title=f"Drift detected in {alert.span_kind} spans",
                            body=f"PSI score: {alert.psi_score:.3f}, severity: {alert.severity}",
                            reference_id=alert.id,
                        )

                        await manager.broadcast(
                            ps.project_id,
                            {
                                "type": "drift.alert",
                                "data": {
                                    "alert_id": alert.id,
                                    "span_kind": alert.span_kind,
                                    "psi_score": alert.psi_score,
                                    "severity": alert.severity,
                                },
                            },
                        )

                    if alerts:
                        logger.info(
                            "Drift check for project %s found %d alerts",
                            ps.project_id,
                            len(alerts),
                        )
            except Exception:
                logger.exception("Drift check failed for project %s", ps.project_id)


# Singleton
drift_scheduler = DriftScheduler()
