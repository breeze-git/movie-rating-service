from collections.abc import Mapping
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.models import Director
from app.schemas.common import DirectorBrief

from .base import BaseRepository


class DirectorRepository(BaseRepository):
    model = Director

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

    async def update(self, director: Director, director_data: Mapping[str, Any]):
        for key, value in director_data.items():
            setattr(director, key, value)

        await self._flush()
