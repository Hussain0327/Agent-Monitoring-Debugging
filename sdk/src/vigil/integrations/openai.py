"""OpenAI monkey-patch instrumentation.

Patches ``ChatCompletion.create`` and ``AsyncCompletions.create`` to
automatically capture LLM spans with input/output data.  Sync patches
use the thread-safe ``end_span_sync`` to avoid event-loop conflicts.
"""

from __future__ import annotations

import functools
import logging
from typing import Any

from vigil._client import get_client
from vigil._types import SpanKind, SpanStatus
from vigil.integrations import register

logger = logging.getLogger("vigil.integrations.openai")

_original_create: Any = None
_original_acreate: Any = None


def _extract_input(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Extract relevant input fields from an OpenAI chat completion request."""
    return {
        "model": kwargs.get("model", ""),
        "messages": kwargs.get("messages", []),
        "temperature": kwargs.get("temperature"),
        "max_tokens": kwargs.get("max_tokens"),
    }


def _extract_output(response: Any) -> dict[str, Any]:
    """Extract relevant output fields from an OpenAI chat completion response."""
    try:
        choice = response.choices[0]
        return {
            "model": response.model,
            "content": choice.message.content,
            "role": choice.message.role,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }
    except (AttributeError, IndexError):
        return {"raw": str(response)}


def _patch() -> None:
    """Monkey-patch OpenAI's Completions.create and AsyncCompletions.create."""
    global _original_create, _original_acreate

    try:
        from openai.resources.chat.completions import Completions
    except ImportError:
        logger.debug("openai not installed, skipping integration")
        return

    _original_create = Completions.create

    @functools.wraps(_original_create)
    def patched_create(self: Any, *args: Any, **kwargs: Any) -> Any:
        client = get_client()
        if not client:
            return _original_create(self, *args, **kwargs)

        span = client.start_span("openai.chat.completions", kind=SpanKind.LLM)
        span.set_input(_extract_input(kwargs))
        try:
            response = _original_create(self, *args, **kwargs)
            span.set_output(_extract_output(response))
            client.end_span_sync(span, status=SpanStatus.OK)
            return response
        except Exception as exc:
            span.set_output({"error": str(exc)})
            client.end_span_sync(span, status=SpanStatus.ERROR)
            raise

    Completions.create = patched_create  # type: ignore[method-assign]

    # Patch async if available (openai >=1.0 uses AsyncCompletions)
    try:
        from openai.resources.chat.completions import AsyncCompletions

        _original_acreate = AsyncCompletions.create

        @functools.wraps(_original_acreate)
        async def patched_acreate(self: Any, *args: Any, **kwargs: Any) -> Any:
            client = get_client()
            if not client:
                return await _original_acreate(self, *args, **kwargs)

            span = client.start_span("openai.chat.completions", kind=SpanKind.LLM)
            span.set_input(_extract_input(kwargs))
            try:
                response = await _original_acreate(self, *args, **kwargs)
                span.set_output(_extract_output(response))
                await client.end_span(span, status=SpanStatus.OK)
                return response
            except Exception as exc:
                span.set_output({"error": str(exc)})
                await client.end_span(span, status=SpanStatus.ERROR)
                raise

        AsyncCompletions.create = patched_acreate  # type: ignore[method-assign]
    except ImportError:
        pass

    logger.info("OpenAI integration activated")


register("openai", _patch)
