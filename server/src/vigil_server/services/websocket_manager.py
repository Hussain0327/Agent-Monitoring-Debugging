"""WebSocket connection manager for per-project real-time broadcasts."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("vigil_server.services.websocket")


class ConnectionManager:
    """Manages WebSocket connections grouped by project_id."""

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = {}

    async def connect(self, ws: WebSocket, project_id: str) -> None:
        """Accept and register a WebSocket connection."""
        await ws.accept()
        if project_id not in self._connections:
            self._connections[project_id] = set()
        self._connections[project_id].add(ws)
        logger.debug(
            "WS connected for project %s (total=%d)", project_id, len(self._connections[project_id])
        )

    def disconnect(self, ws: WebSocket, project_id: str) -> None:
        """Remove a WebSocket connection."""
        if project_id in self._connections:
            self._connections[project_id].discard(ws)
            if not self._connections[project_id]:
                del self._connections[project_id]

    async def broadcast(self, project_id: str, message: dict[str, Any]) -> None:
        """Send a message to all connections for a project."""
        if project_id not in self._connections:
            return

        dead: list[WebSocket] = []
        for ws in self._connections[project_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)

        # Prune dead connections
        for ws in dead:
            self._connections[project_id].discard(ws)
        if project_id in self._connections and not self._connections[project_id]:
            del self._connections[project_id]

    def connection_count(self, project_id: str | None = None) -> int:
        """Return the number of active connections."""
        if project_id:
            return len(self._connections.get(project_id, set()))
        return sum(len(v) for v in self._connections.values())


# Singleton instance
manager = ConnectionManager()
