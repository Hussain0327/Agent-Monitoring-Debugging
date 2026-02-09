"""WebSocket endpoint for real-time updates."""

from __future__ import annotations

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from vigil_server.services.auth_service import decode_token
from vigil_server.services.websocket_manager import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    ws: WebSocket,
    token: str = Query(...),
) -> None:
    """WebSocket endpoint for real-time project updates.

    Authenticates via token query parameter (JWT or API key).
    """
    # Validate token
    project_id = await _resolve_project_id(token)
    if not project_id:
        await ws.close(code=4001, reason="Invalid token")
        return

    await manager.connect(ws, project_id)
    try:
        while True:
            data = await ws.receive_json()
            # Handle client pings
            if data.get("type") == "ping":
                await ws.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(ws, project_id)
    except Exception:
        manager.disconnect(ws, project_id)


async def _resolve_project_id(token: str) -> str | None:
    """Resolve a token to a project_id. Returns None if invalid."""
    from vigil_server.config import settings

    # Try JWT
    subject = decode_token(token)
    if subject is not None:
        return "default"

    # Try dev API key
    if token == settings.api_key:
        return "default"

    # Try database API key
    from sqlalchemy import select

    from vigil_server.db.session import async_session
    from vigil_server.models.project import APIKey

    async with async_session() as session:
        stmt = select(APIKey).where(APIKey.key == token, APIKey.is_active == True)  # noqa: E712
        result = await session.execute(stmt)
        key_record = result.scalar_one_or_none()
        return key_record.project_id if key_record else None
