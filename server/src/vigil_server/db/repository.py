"""Generic async CRUD repository with error handling."""

from __future__ import annotations

import logging
from typing import Any, Generic, Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from vigil_server.exceptions import VigilError
from vigil_server.models.base import Base

logger = logging.getLogger("vigil_server.db.repository")

ModelT = TypeVar("ModelT", bound=Base)


class Repository(Generic[ModelT]):
    """Generic async CRUD operations for SQLAlchemy models."""

    def __init__(self, model: Type[ModelT], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def create(self, **kwargs: Any) -> ModelT:
        """Create and persist a new model instance."""
        try:
            instance = self._model(**kwargs)
            self._session.add(instance)
            await self._session.flush()
            await self._session.refresh(instance)
            return instance
        except SQLAlchemyError:
            logger.exception("Failed to create %s", self._model.__name__)
            raise VigilError(f"Failed to create {self._model.__name__}", status_code=500)

    async def get(self, id: UUID | str) -> ModelT | None:
        """Fetch a model by primary key."""
        try:
            return await self._session.get(self._model, id)
        except SQLAlchemyError:
            logger.exception("Failed to get %s with id=%s", self._model.__name__, id)
            raise VigilError(f"Failed to fetch {self._model.__name__}", status_code=500)

    async def list(
        self,
        offset: int = 0,
        limit: int = 50,
        **filters: Any,
    ) -> Sequence[ModelT]:
        """List models with optional filtering and pagination."""
        try:
            stmt = select(self._model)
            for key, value in filters.items():
                if hasattr(self._model, key) and value is not None:
                    stmt = stmt.where(getattr(self._model, key) == value)
            stmt = stmt.offset(offset).limit(limit)
            result = await self._session.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError:
            logger.exception("Failed to list %s", self._model.__name__)
            raise VigilError(f"Failed to list {self._model.__name__}", status_code=500)

    async def delete(self, id: UUID | str) -> bool:
        """Delete a model by primary key. Returns True if deleted."""
        try:
            instance = await self.get(id)
            if instance:
                await self._session.delete(instance)
                await self._session.flush()
                return True
            return False
        except SQLAlchemyError:
            logger.exception("Failed to delete %s with id=%s", self._model.__name__, id)
            raise VigilError(f"Failed to delete {self._model.__name__}", status_code=500)
