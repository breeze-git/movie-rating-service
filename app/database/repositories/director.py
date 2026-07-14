from collections.abc import Mapping
from typing import Any
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
from app.schemas.common import DirectorBrief

from .pg_error_codes import PostgresErrorCode as pg_err


class DirectorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UUID) -> Director | None:
        query = select(Director).where(Director.id == id)

        director = await self.session.scalar(query)

        return director

    async def get_directors(self, name_search: str | None) -> list[DirectorBrief]:
        if name_search:
            query = select(
                Director.id,
                Director.first_name,
                Director.last_name,
                Director.date_of_birth,
            ).where((Director.first_name + " " + Director.last_name).ilike(f"%{name_search}%"))

        result = await self.session.execute(query)

        rows = result.mappings().all()

        directors = [DirectorBrief.model_validate(row) for row in rows]

        return directors

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

    async def update(self, director: Director, director_data: Mapping[str, Any]):
        for key, value in director_data.items():
            setattr(director, key, value)

        try:
            await self.session.flush()
        except IntegrityError as e:
            sqlstate = getattr(e.orig, "sqlstate", None)

            if sqlstate == pg_err.UNIQUE_VIOLATION:
                raise EntityAlreadyExistsError from None

    async def delete(self, id: UUID) -> None:
        stmt = delete(Director).where(Director.id == id).returning(Director.id)

        result = await self.session.execute(stmt)

        if not result.scalar():
            raise EntityNotFoundError from None
