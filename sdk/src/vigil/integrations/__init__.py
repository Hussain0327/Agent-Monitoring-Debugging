"""Integration registry for third-party library instrumentation."""

from __future__ import annotations

from typing import Callable

_integrations: dict[str, Callable[[], None]] = {}


def register(name: str, activate_fn: Callable[[], None]) -> None:
    _integrations[name] = activate_fn


def activate(name: str) -> None:
    if name in _integrations:
        _integrations[name]()


def activate_all() -> None:
    for fn in _integrations.values():
        fn()


def available() -> list[str]:
    return list(_integrations.keys())
