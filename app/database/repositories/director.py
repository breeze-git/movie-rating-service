from collections.abc import Mapping
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.database.models import Director
from app.schemas.common import CollectionEnvelope, DirectorBrief

from .base import BaseRepository


class DirectorRepository(BaseRepository):
    model = Director

    async def get_directors(
        self, search: str | None = None, limit: int = 10, offset: int = 0
    ) -> CollectionEnvelope[DirectorBrief]:
        query = select(
            Director.id,
            Director.first_name,
            Director.last_name,
            Director.date_of_birth,
        )

        if search:
            query = query.where(func.concat(Director.first_name, " ", Director.last_name).ilike(f"%{search}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)

        rows = result.mappings().all()

        directors = [DirectorBrief.model_validate(row) for row in rows]

        collection = CollectionEnvelope(
            items=directors,
            total=total,
        )

        return collection

    async def get_by_id_with_relations(self, director_id: UUID) -> Director | None:
        query = select(Director).where(Director.id == director_id).options(selectinload(Director.movies))

        director = await self.session.scalar(query)

        return director

    async def update(self, director: Director, update_data: Mapping[str, Any]):
        for key, value in update_data.items():
            setattr(director, key, value)

        await self._flush()
