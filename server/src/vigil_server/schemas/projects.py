"""Pydantic schemas for project management."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    name: str = Field(..., min_length=1, max_length=256)
    description: str = Field(default="", max_length=1024)


class APIKeyResponse(BaseModel):
    """Schema for an API key in responses."""

    id: str
    key: str
    name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    """Schema for a project in responses."""

    id: str
    name: str
    description: str
    created_at: datetime
    api_keys: list[APIKeyResponse] = []

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """Paginated project list response."""

    projects: list[ProjectResponse]
    total: int
