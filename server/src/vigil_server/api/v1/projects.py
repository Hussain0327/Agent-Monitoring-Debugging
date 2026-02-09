"""Project CRUD and API key management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from vigil_server.dependencies import CurrentProject, DBSession, GuestProject  # noqa: TC001
from vigil_server.models.project import APIKey, Project
from vigil_server.models.project_settings import ProjectSettings
from vigil_server.schemas.project_settings import ProjectSettingsResponse, ProjectSettingsUpdate
from vigil_server.schemas.projects import ProjectCreate, ProjectListResponse, ProjectResponse
from vigil_server.services.encryption import decrypt, encrypt, mask_key

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreate,
    db: DBSession,
    _project_id: CurrentProject,
) -> ProjectResponse:
    """Create a new project with an initial API key."""
    project = Project(name=body.name, description=body.description)
    db.add(project)
    await db.flush()

    # Create default API key
    api_key = APIKey(project_id=project.id, name="default")
    db.add(api_key)
    await db.flush()
    await db.refresh(project)

    return ProjectResponse.model_validate(project)


@router.get("")
async def list_projects(db: DBSession, _project_id: GuestProject) -> ProjectListResponse:
    """List all projects."""
    count_result = await db.execute(select(func.count()).select_from(Project))
    total = count_result.scalar() or 0

    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    projects = result.scalars().all()

    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=total,
    )


@router.get("/{project_id}")
async def get_project(project_id: str, db: DBSession, _auth: GuestProject) -> ProjectResponse:
    """Get a project by ID."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.post("/{project_id}/rotate-key", status_code=status.HTTP_201_CREATED)
async def rotate_api_key(
    project_id: str,
    db: DBSession,
    _auth: CurrentProject,
) -> dict[str, str]:
    """Deactivate all existing keys and create a new one."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Deactivate existing keys
    for key in project.api_keys:
        key.is_active = False

    # Create new key
    new_key = APIKey(project_id=project_id, name="rotated")
    db.add(new_key)
    await db.flush()

    return {"key": new_key.key}


def _build_settings_response(s: ProjectSettings) -> ProjectSettingsResponse:
    """Build a settings response with masked keys."""
    openai_set = s.openai_api_key_encrypted is not None
    anthropic_set = s.anthropic_api_key_encrypted is not None
    return ProjectSettingsResponse(
        id=s.id,
        project_id=s.project_id,
        openai_api_key_set=openai_set,
        openai_api_key_masked=mask_key(decrypt(s.openai_api_key_encrypted)) if openai_set else None,
        anthropic_api_key_set=anthropic_set,
        anthropic_api_key_masked=(
            mask_key(decrypt(s.anthropic_api_key_encrypted)) if anthropic_set else None
        ),
        default_openai_model=s.default_openai_model,
        default_anthropic_model=s.default_anthropic_model,
        drift_check_interval_minutes=s.drift_check_interval_minutes,
        drift_check_enabled=s.drift_check_enabled,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


@router.get("/{project_id}/settings")
async def get_settings(
    project_id: str,
    db: DBSession,
    _auth: GuestProject,
) -> ProjectSettingsResponse:
    """Get project settings."""
    stmt = select(ProjectSettings).where(ProjectSettings.project_id == project_id)
    result = await db.execute(stmt)
    s = result.scalar_one_or_none()
    if not s:
        # Auto-create default settings
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        s = ProjectSettings(project_id=project_id)
        db.add(s)
        await db.flush()
        await db.refresh(s)
    return _build_settings_response(s)


@router.put("/{project_id}/settings")
async def update_settings(
    project_id: str,
    body: ProjectSettingsUpdate,
    db: DBSession,
    _auth: CurrentProject,
) -> ProjectSettingsResponse:
    """Update project settings."""
    stmt = select(ProjectSettings).where(ProjectSettings.project_id == project_id)
    result = await db.execute(stmt)
    s = result.scalar_one_or_none()
    if not s:
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        s = ProjectSettings(project_id=project_id)
        db.add(s)
        await db.flush()

    if body.openai_api_key is not None:
        s.openai_api_key_encrypted = encrypt(body.openai_api_key)
    if body.anthropic_api_key is not None:
        s.anthropic_api_key_encrypted = encrypt(body.anthropic_api_key)
    if body.default_openai_model is not None:
        s.default_openai_model = body.default_openai_model
    if body.default_anthropic_model is not None:
        s.default_anthropic_model = body.default_anthropic_model
    if body.drift_check_interval_minutes is not None:
        s.drift_check_interval_minutes = body.drift_check_interval_minutes
    if body.drift_check_enabled is not None:
        s.drift_check_enabled = body.drift_check_enabled

    await db.flush()
    await db.refresh(s)
    return _build_settings_response(s)
