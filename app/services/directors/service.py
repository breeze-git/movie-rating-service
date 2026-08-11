import logging
from uuid import UUID

from fastapi import Depends

from app.cache.decorators import cached, invalidate_cache
from app.core.exceptions.repository import RepoUniqueViolationError
from app.database.models import Director
from app.database.uow import UnitOfWork
from app.schemas.common import CollectionEnvelope, DirectorBrief, PaginationParams
from app.schemas.directors import DirectorBase, DirectorDetail, DirectorUpdate
from app.services.directors.exceptions import (
    DirectorAlreadyExistsError,
    DirectorNotFoundError,
)

logger = logging.getLogger(__name__)


class DirectorService:
    def __init__(self, uow: UnitOfWork = Depends()):
        self.uow = uow

    @cached(key="director:{director_id}", schema=DirectorDetail)
    async def get_director_by_id(self, director_id: UUID) -> DirectorDetail:
        async with self.uow:
            db_director = await self.uow.directors.get_by_id_with_relations(director_id)

            if db_director is None:
                raise DirectorNotFoundError(director_id) from None

            director = DirectorDetail.model_validate(db_director)

            return director

    async def get_directors(
        self, search: str | None, pagination: PaginationParams
    ) -> CollectionEnvelope[DirectorBrief]:
        async with self.uow:
            director_collection = await self.uow.directors.get_directors(
                search=search,
                limit=pagination.limit,
                offset=pagination.offset,
            )

            return director_collection

    async def create_director(self, dto: DirectorBase) -> DirectorBrief:
        async with self.uow:
            db_director = Director(**dto.model_dump())

            try:
                await self.uow.directors.save(db_director)
            except RepoUniqueViolationError as e:
                raise DirectorAlreadyExistsError(conflict_value=dto.model_dump()) from e

            director = DirectorBrief.model_validate(db_director)

            logger.info(
                "Director created",
                extra={"id": director.id},
            )

            return director

    @invalidate_cache(key="director:{director_id}")
    async def update_director(self, director_id: UUID, dto: DirectorUpdate) -> DirectorBrief:
        async with self.uow:
            db_director = await self.uow.directors.get_by_id(director_id)

            if db_director is None:
                raise DirectorNotFoundError(director_id) from None

            update_data = dto.model_dump(exclude_unset=True)

            try:
                await self.uow.directors.update(db_director, update_data)
            except RepoUniqueViolationError as e:
                raise DirectorAlreadyExistsError(conflict_value=update_data) from e

            director = DirectorBrief.model_validate(db_director)

            return director

    @invalidate_cache(key="director:{director_id}")
    async def remove_director(self, director_id: UUID) -> None:
        async with self.uow:
            result = await self.uow.directors.delete(director_id)

            if not result.scalar():
                raise DirectorNotFoundError(director_id) from None

            logger.info(
                "Director deleted",
                extra={"id": director_id},
            )
