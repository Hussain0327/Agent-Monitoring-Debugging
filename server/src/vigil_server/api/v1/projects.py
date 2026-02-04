"""Project CRUD and API key management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from vigil_server.dependencies import CurrentProject, DBSession  # noqa: TC001
from vigil_server.models.project import APIKey, Project
from vigil_server.schemas.projects import ProjectCreate, ProjectListResponse, ProjectResponse

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
async def list_projects(db: DBSession, _project_id: CurrentProject) -> ProjectListResponse:
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
async def get_project(project_id: str, db: DBSession, _auth: CurrentProject) -> ProjectResponse:
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
