"""Trace ingestion and query endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from vigil_server.dependencies import CurrentProject, DBSession
from vigil_server.schemas.traces import (
    IngestRequest,
    IngestResponse,
    TraceListResponse,
    TraceResponse,
)
from vigil_server.services.trace_service import (
    build_trace_response,
    get_trace,
    ingest_spans,
    list_traces,
)

router = APIRouter(prefix="/traces", tags=["traces"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def ingest(
    request: IngestRequest,
    db: DBSession,
    project_id: CurrentProject,
) -> IngestResponse:
    """Ingest spans from the SDK."""
    trace_id, count = await ingest_spans(db, request, project_id)
    return IngestResponse(trace_id=trace_id, span_count=count)


@router.get("")
async def list_all(
    db: DBSession,
    project_id: CurrentProject,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> TraceListResponse:
    """List traces with pagination."""
    traces, total = await list_traces(db, project_id, offset, limit)
    return TraceListResponse(
        traces=[build_trace_response(t) for t in traces],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{trace_id}")
async def get_one(
    trace_id: str,
    db: DBSession,
    project_id: CurrentProject,
) -> TraceResponse:
    """Get a single trace with all spans."""
    trace = await get_trace(db, trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return build_trace_response(trace)
