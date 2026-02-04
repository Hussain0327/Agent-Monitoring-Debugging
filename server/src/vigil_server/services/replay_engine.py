"""Trace replay engine: load a trace, apply mutations, compute diff."""

from __future__ import annotations

import copy
import logging
from typing import TYPE_CHECKING, Any

from sqlalchemy.exc import SQLAlchemyError

from vigil_server.exceptions import NotFoundError, VigilError
from vigil_server.models.replay import ReplayRun
from vigil_server.models.trace import Trace as TraceModel
from vigil_server.schemas.replay import ReplayDiffResponse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("vigil_server.services.replay")


class ReplayResult:
    """Container for replay output including mutations and diffs."""

    def __init__(
        self,
        original_trace_id: str,
        mutations: dict[str, Any],
        diffs: list[dict[str, Any]],
        replay_run_id: str | None = None,
    ) -> None:
        self.original_trace_id = original_trace_id
        self.mutations = mutations
        self.diffs = diffs
        self.replay_run_id = replay_run_id

    def to_dict(self) -> dict[str, Any]:
        """Serialise the replay result to a dictionary."""
        result: dict[str, Any] = {
            "original_trace_id": self.original_trace_id,
            "mutations": self.mutations,
            "diffs": self.diffs,
        }
        if self.replay_run_id:
            result["replay_run_id"] = self.replay_run_id
        return result


async def replay_trace(
    session: AsyncSession,
    trace_id: str,
    mutations: dict[str, Any] | None = None,
) -> ReplayResult:
    """Load a trace, apply mutations to span inputs, and compute output diffs.

    Persists a ReplayRun record for each replay execution.
    """
    try:
        trace = await session.get(TraceModel, trace_id)
    except SQLAlchemyError as exc:
        logger.exception("Database error loading trace %s for replay", trace_id)
        raise VigilError("Failed to load trace for replay", status_code=500) from exc

    if not trace:
        raise NotFoundError("Trace", trace_id)

    mutations = mutations or {}
    diffs: list[dict[str, Any]] = []

    for span in trace.spans:
        if span.id in mutations:
            original_input = copy.deepcopy(span.input) or {}
            mutated_input = {**original_input, **mutations[span.id]}
            diffs.append(
                {
                    "span_id": span.id,
                    "span_name": span.name,
                    "original_input": original_input,
                    "mutated_input": mutated_input,
                    "original_output": span.output,
                    "note": "Replay would re-execute this span with mutated input",
                }
            )

    # Persist replay run
    replay_run = ReplayRun(
        original_trace_id=trace_id,
        status="completed",
        config={"mutations": mutations, "diffs": diffs},
    )
    session.add(replay_run)
    await session.flush()

    logger.debug(
        "Replayed trace %s with %d mutations (run=%s)", trace_id, len(mutations), replay_run.id
    )
    return ReplayResult(
        original_trace_id=trace_id,
        mutations=mutations,
        diffs=diffs,
        replay_run_id=replay_run.id,
    )


async def get_replay_run(session: AsyncSession, replay_id: str) -> ReplayRun | None:
    """Fetch a replay run by ID."""
    try:
        return await session.get(ReplayRun, replay_id)
    except SQLAlchemyError as exc:
        logger.exception("Database error fetching replay run %s", replay_id)
        raise VigilError("Failed to fetch replay run", status_code=500) from exc


async def get_replay_diff(
    session: AsyncSession, trace_id: str, replay_id: str
) -> ReplayDiffResponse | None:
    """Fetch the diff from a completed replay run."""
    run = await get_replay_run(session, replay_id)
    if not run or run.original_trace_id != trace_id:
        return None

    config = run.config or {}
    return ReplayDiffResponse(
        original_trace_id=run.original_trace_id,
        mutations=config.get("mutations", {}),
        diffs=config.get("diffs", []),
    )
