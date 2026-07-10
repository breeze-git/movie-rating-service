from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions.repositories import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.database.models import Director

from .pg_error_codes import PostgresErrorCode as pg_err


class DirectorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UUID) -> Director | None:
        query = select(Director).where(Director.id == id)

        director = await self.session.scalar(query)

        return director

    async def get_directors(self, name_search: str | None) -> Sequence[Director]:
        if name_search:
            query = select(Director).where((Director.first_name + " " + Director.last_name).like(f"%{name_search}%"))

        result = await self.session.scalars(query)

        return result.all()

    async def get_by_id_with_relations(self, id: UUID) -> Director | None:
        query = select(Director).where(Director.id == id).options(selectinload(Director.movies))

        director = await self.session.scalar(query)

        return director

    async def save(self, director: Director) -> None:
        self.session.add(director)

        try:
            await self.session.flush()
        except IntegrityError as e:
            sqlstate = getattr(e.orig, "sqlstate", None)

            if sqlstate == pg_err.UNIQUE_VIOLATION:
                raise EntityAlreadyExistsError from None

    async def update(self, director: Director, director_data_dict: dict):
        for key, value in director_data_dict.items():
            setattr(director, key, value)

        try:
            await self.session.flush()
        except IntegrityError as e:
            sqlstate = getattr(e.orig, "sqlstate", None)

            if sqlstate == pg_err.UNIQUE_VIOLATION:
                raise EntityAlreadyExistsError from None

    async def delete(self, id: UUID) -> None:
        stmt = delete(Director).where(Director.id == id)

        result = await self.session.execute(stmt)

        if not result.rowcount:  # type: ignore
            raise EntityNotFoundError from None
