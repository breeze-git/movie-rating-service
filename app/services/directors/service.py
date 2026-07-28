import logging
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.repository import RepoUniqueViolationError
from app.database.models import Director
from app.database.repositories.director import DirectorRepository
from app.database.session import get_session
from app.schemas.common import CollectionEnvelope, DirectorBrief, PaginationParams
from app.schemas.directors import DirectorBase, DirectorDetail, DirectorUpdate
from app.services.directors.exceptions import (
    DirectorAlreadyExistsError,
    DirectorNotFoundError,
)

logger = logging.getLogger(__name__)


class DirectorService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

        self.directors = DirectorRepository(session)

    async def get_director_by_id(self, director_id: UUID) -> DirectorDetail:
        db_director = await self.directors.get_by_id_with_relations(director_id)

        if db_director is None:
            raise DirectorNotFoundError(director_id) from None

        director = DirectorDetail.model_validate(db_director)

        return director

    async def get_directors(
        self, search: str | None, pagination: PaginationParams
    ) -> CollectionEnvelope[DirectorBrief]:
        director_collection = await self.directors.get_directors(
            search=search,
            limit=pagination.limit,
            offset=pagination.offset,
        )

        return director_collection

    async def create_director(self, dto: DirectorBase) -> DirectorBrief:
        db_director = Director(**dto.model_dump())

        try:
            await self.directors.save(db_director)
        except RepoUniqueViolationError as e:
            raise DirectorAlreadyExistsError(conflict_value=dto.model_dump()) from e

        await self.session.commit()

        director = DirectorBrief.model_validate(db_director)

        logger.info(
            "Director created",
            extra={"id": director.id},
        )

        return director

    async def update_director(self, director_id: UUID, dto: DirectorUpdate) -> DirectorBrief:
        db_director = await self.directors.get_by_id(director_id)

        if db_director is None:
            raise DirectorNotFoundError(director_id) from None

        update_data = dto.model_dump(exclude_unset=True)

        try:
            await self.directors.update(db_director, update_data)
        except RepoUniqueViolationError as e:
            raise DirectorAlreadyExistsError(conflict_value=update_data) from e

        await self.session.commit()

        director = DirectorBrief.model_validate(db_director)

        return director

    async def remove_director(self, director_id: UUID) -> None:
        result = await self.directors.delete(director_id)

        if not result.scalar():
            raise DirectorNotFoundError(director_id) from None

        await self.session.commit()

        logger.info(
            "Director deleted",
            extra={"id": director_id},
        )
