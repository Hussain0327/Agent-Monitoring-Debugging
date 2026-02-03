"""API key extraction and validation.

This module re-exports the authentication logic from
:mod:`vigil_server.dependencies` to avoid duplication.  The canonical
implementation lives in ``dependencies.py`` because it is used as a
FastAPI dependency and has proper access to the database session.
"""

from __future__ import annotations

# Re-export the dependency-based auth for any code that imports from here
from vigil_server.dependencies import get_current_project

# Paths that don't require authentication (used by CORS preflight, docs, etc.)
PUBLIC_PATHS = {"/health", "/ready", "/docs", "/openapi.json", "/redoc"}

__all__ = ["get_current_project", "PUBLIC_PATHS"]
