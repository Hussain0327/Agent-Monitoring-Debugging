"""Notification endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from vigil_server.dependencies import CurrentProject, DBSession  # noqa: TC001
from vigil_server.schemas.notifications import NotificationCountResponse, NotificationResponse
from vigil_server.services.notification_service import (
    list_notifications,
    mark_all_read,
    mark_read,
    unread_count,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
async def list_all(
    db: DBSession,
    project_id: CurrentProject,
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[NotificationResponse]:
    """List notifications for the current project."""
    items = await list_notifications(
        db, project_id, unread_only=unread_only, limit=limit, offset=offset
    )
    return [NotificationResponse.model_validate(n) for n in items]


@router.patch("/{notification_id}/read")
async def read_one(
    notification_id: str,
    db: DBSession,
    _auth: CurrentProject,
) -> NotificationResponse:
    """Mark a notification as read."""
    notification = await mark_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse.model_validate(notification)


@router.post("/read-all")
async def read_all(
    db: DBSession,
    project_id: CurrentProject,
) -> dict[str, int]:
    """Mark all notifications as read for the current project."""
    count = await mark_all_read(db, project_id)
    return {"marked_read": count}


@router.get("/count")
async def count(
    db: DBSession,
    project_id: CurrentProject,
) -> NotificationCountResponse:
    """Get unread notification count."""
    n = await unread_count(db, project_id)
    return NotificationCountResponse(unread=n)
