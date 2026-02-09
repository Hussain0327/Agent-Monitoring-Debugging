"""Notification CRUD service."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlalchemy import func, select, update

from vigil_server.models.notification import Notification

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("vigil_server.services.notification")


async def create_notification(
    session: AsyncSession,
    *,
    project_id: str,
    type: str,
    title: str,
    body: str = "",
    reference_id: str | None = None,
) -> Notification:
    """Create and return a new notification."""
    notification = Notification(
        project_id=project_id,
        type=type,
        title=title,
        body=body,
        reference_id=reference_id,
    )
    session.add(notification)
    await session.flush()
    logger.debug("Created notification %s for project %s", notification.id, project_id)
    return notification


async def list_notifications(
    session: AsyncSession,
    project_id: str,
    *,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Notification]:
    """List notifications for a project."""
    stmt = (
        select(Notification)
        .where(Notification.project_id == project_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if unread_only:
        stmt = stmt.where(Notification.read == False)  # noqa: E712
    result = await session.execute(stmt)
    return result.scalars().all()


async def mark_read(session: AsyncSession, notification_id: str) -> Notification | None:
    """Mark a single notification as read."""
    notification = await session.get(Notification, notification_id)
    if notification:
        notification.read = True
        await session.flush()
    return notification


async def mark_all_read(session: AsyncSession, project_id: str) -> int:
    """Mark all notifications for a project as read. Returns count updated."""
    stmt = (
        update(Notification)
        .where(Notification.project_id == project_id, Notification.read == False)  # noqa: E712
        .values(read=True)
    )
    result = await session.execute(stmt)
    await session.flush()
    return result.rowcount


async def unread_count(session: AsyncSession, project_id: str) -> int:
    """Return the count of unread notifications."""
    stmt = (
        select(func.count())
        .select_from(Notification)
        .where(
            Notification.project_id == project_id,
            Notification.read == False,  # noqa: E712
        )
    )
    result = await session.execute(stmt)
    return result.scalar() or 0
