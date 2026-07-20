from typing import Any, Generic, Protocol, TypeVar, runtime_checkable
from uuid import UUID

from sqlalchemy import Result, delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped

from app.database.exceptions_translator import parse_integrity_error


@runtime_checkable
class Identifiable(Protocol):
    id: Mapped[UUID | int]


ModelT = TypeVar("ModelT", bound=Identifiable)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _execute(self, stmt: Any) -> Result[Any]:
        try:
            result = await self.session.execute(stmt)
        except IntegrityError as e:
            raise parse_integrity_error(e) from e

        return result

    async def _flush(self) -> None:
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise parse_integrity_error(e) from e

    async def get_by_id(self, entity_id: UUID | int) -> ModelT | None:
        query = select(self.model).where(self.model.id == entity_id)

        result = await self._execute(query)

        return result.scalar()

    async def save(self, model: ModelT) -> None:
        self.session.add(model)

        await self._flush()

    async def delete(self, entity_id) -> Result[Any]:
        stmt = delete(self.model).where(self.model.id == entity_id).returning(self.model.id)

        result = await self._execute(stmt)

        return result
