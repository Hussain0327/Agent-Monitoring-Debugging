"""Pydantic schemas for project settings."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ProjectSettingsUpdate(BaseModel):
    """Schema for updating project settings."""

    openai_api_key: str | None = Field(
        default=None, description="OpenAI API key (will be encrypted at rest)"
    )
    anthropic_api_key: str | None = Field(
        default=None, description="Anthropic API key (will be encrypted at rest)"
    )
    default_openai_model: str | None = Field(default=None, max_length=128)
    default_anthropic_model: str | None = Field(default=None, max_length=128)
    drift_check_interval_minutes: int | None = Field(default=None, ge=5, le=1440)
    drift_check_enabled: bool | None = None


class ProjectSettingsResponse(BaseModel):
    """Schema for project settings in responses. API keys are masked."""

    id: str
    project_id: str
    openai_api_key_set: bool = False
    openai_api_key_masked: str | None = None
    anthropic_api_key_set: bool = False
    anthropic_api_key_masked: str | None = None
    default_openai_model: str
    default_anthropic_model: str
    drift_check_interval_minutes: int
    drift_check_enabled: bool
    created_at: datetime
    updated_at: datetime
