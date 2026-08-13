from typing import Any, Generic, Protocol, TypeVar, runtime_checkable
from uuid import UUID

from asyncpg import UniqueViolationError
from sqlalchemy import Result, delete, exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped

from app.core.exceptions.repository import RepoError, RepoUniqueViolationError


@runtime_checkable
class Identifiable(Protocol):
    id: Mapped[UUID | int]


ModelT = TypeVar("ModelT", bound=Identifiable)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    def _translate_integrity_error(self, exc: IntegrityError) -> RepoError:
        """Translate SQLAlchemy IntegrityError into repository exceptions.

        Used internally by _execute() and _flush().
        Subclasses should use those methods instead of calling this helper directly.
        """

        sqlstate = getattr(exc.orig, "sqlstate", None)
        err_msg = str(exc.orig)

        if sqlstate == UniqueViolationError.sqlstate:
            return RepoUniqueViolationError(detail=err_msg)

        return RepoError(detail=err_msg)

    async def _execute(self, stmt: Any) -> Result[Any]:
        try:
            result = await self.session.execute(stmt)
        except IntegrityError as e:
            raise self._translate_integrity_error(exc=e) from e

        return result

    async def _flush(self) -> None:
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise self._translate_integrity_error(exc=e) from e

    async def get_by_id(self, entity_id: UUID | int) -> ModelT | None:
        query = select(self.model).where(self.model.id == entity_id)

        result = await self._execute(query)

        return result.scalar()

    async def save(self, model: ModelT) -> None:
        self.session.add(model)

        await self._flush()

    async def exists_by_id(self, entity_id: UUID | int) -> bool:
        stmt = select(exists().where(self.model.id == entity_id))

        result = await self._execute(stmt)

        existed = bool(result.scalar())

        return existed

    async def delete(self, entity_id: UUID | int) -> Result[Any]:
        stmt = delete(self.model).where(self.model.id == entity_id).returning(self.model.id)

        result = await self._execute(stmt)

        return result
