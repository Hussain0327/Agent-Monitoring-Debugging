"""Pydantic schemas for notifications."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    """Schema for a notification in responses."""

    id: str
    project_id: str
    type: str
    title: str
    body: str
    reference_id: str | None
    read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationCountResponse(BaseModel):
    """Schema for unread notification count."""

    unread: int
