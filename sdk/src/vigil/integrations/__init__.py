"""Integration registry for third-party library instrumentation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

_integrations: dict[str, Callable[[], None]] = {}


def register(name: str, activate_fn: Callable[[], None]) -> None:
    _integrations[name] = activate_fn


def activate(name: str) -> None:
    _ensure_loaded()
    if name in _integrations:
        _integrations[name]()


def activate_all() -> None:
    _ensure_loaded()
    for fn in _integrations.values():
        fn()


def available() -> list[str]:
    _ensure_loaded()
    return list(_integrations.keys())


_loaded = False


def _ensure_loaded() -> None:
    """Import built-in integration modules so they self-register."""
    global _loaded
    if _loaded:
        return
    _loaded = True
    import vigil.integrations.anthropic as _  # noqa: F811, F401
    import vigil.integrations.openai as _  # noqa: F811, F401
