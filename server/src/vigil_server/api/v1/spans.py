"""Span query endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from vigil_server.dependencies import CurrentProject, DBSession  # noqa: TC001
from vigil_server.models.span import Span as SpanModel
from vigil_server.models.trace import Trace as TraceModel
from vigil_server.schemas.spans import SpanListResponse, SpanResponse

router = APIRouter(prefix="/spans", tags=["spans"])


@router.get("")
async def list_spans(
    db: DBSession,
    project_id: CurrentProject,
    kind: str | None = None,
    status: str | None = None,
    trace_id: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> SpanListResponse:
    """Query spans across traces with filters."""
    stmt = (
        select(SpanModel)
        .join(SpanModel.trace)
        .where(TraceModel.project_id == project_id)
        .order_by(SpanModel.created_at.desc())
    )
    count_stmt = (
        select(func.count())
        .select_from(SpanModel)
        .join(SpanModel.trace)
        .where(TraceModel.project_id == project_id)
    )

    if kind:
        stmt = stmt.where(SpanModel.kind == kind)
        count_stmt = count_stmt.where(SpanModel.kind == kind)
    if status:
        stmt = stmt.where(SpanModel.status == status)
        count_stmt = count_stmt.where(SpanModel.status == status)
    if trace_id:
        stmt = stmt.where(SpanModel.trace_id == trace_id)
        count_stmt = count_stmt.where(SpanModel.trace_id == trace_id)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    result = await db.execute(stmt.offset(offset).limit(limit))
    spans = result.scalars().all()

    return SpanListResponse(
        spans=[
            SpanResponse(
                id=s.id,
                trace_id=s.trace_id,
                parent_span_id=s.parent_span_id,
                name=s.name,
                kind=s.kind,
                status=s.status,
                input=s.input,
                output=s.output,
                metadata=s.metadata_ or {},
                events=s.events or [],
                start_time=s.start_time,
                end_time=s.end_time,
                created_at=s.created_at,
            )
            for s in spans
        ],
        total=total,
        offset=offset,
        limit=limit,
    )
