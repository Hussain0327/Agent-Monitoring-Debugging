"""Trace replay engine: load a trace, apply mutations, compute diff."""

from __future__ import annotations

import copy
import logging
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from vigil_server.exceptions import NotFoundError, VigilError
from vigil_server.models.trace import Trace as TraceModel

logger = logging.getLogger("vigil_server.services.replay")


class ReplayResult:
    """Container for replay output including mutations and diffs."""

    def __init__(
        self,
        original_trace_id: str,
        mutations: dict[str, Any],
        diffs: list[dict[str, Any]],
    ) -> None:
        self.original_trace_id = original_trace_id
        self.mutations = mutations
        self.diffs = diffs

    def to_dict(self) -> dict[str, Any]:
        """Serialise the replay result to a dictionary."""
        return {
            "original_trace_id": self.original_trace_id,
            "mutations": self.mutations,
            "diffs": self.diffs,
        }


async def replay_trace(
    session: AsyncSession,
    trace_id: str,
    mutations: dict[str, Any] | None = None,
) -> ReplayResult:
    """Load a trace, apply mutations to span inputs, and compute output diffs.

    Args:
        session: Database session.
        trace_id: ID of the trace to replay.
        mutations: Dict mapping span_id -> {field: new_value} for input overrides.

    Returns:
        ReplayResult with original trace, mutations applied, and diffs.

    Raises:
        NotFoundError: If the trace does not exist.
    """
    try:
        trace = await session.get(TraceModel, trace_id)
    except SQLAlchemyError:
        logger.exception("Database error loading trace %s for replay", trace_id)
        raise VigilError("Failed to load trace for replay", status_code=500)

    if not trace:
        raise NotFoundError("Trace", trace_id)

    mutations = mutations or {}
    diffs: list[dict[str, Any]] = []

    for span in trace.spans:
        if span.id in mutations:
            original_input = copy.deepcopy(span.input) or {}
            mutated_input = {**original_input, **mutations[span.id]}
            diffs.append({
                "span_id": span.id,
                "span_name": span.name,
                "original_input": original_input,
                "mutated_input": mutated_input,
                "original_output": span.output,
                "note": "Replay would re-execute this span with mutated input",
            })

    logger.debug("Replayed trace %s with %d mutations", trace_id, len(mutations))
    return ReplayResult(
        original_trace_id=trace_id,
        mutations=mutations,
        diffs=diffs,
    )
