from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.error_messages import DirectorMessages
from app.core.exceptions.repositories import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.core.exceptions.services import AlreadyExistsError, NotFoundError
from app.database.models import Director
from app.database.repositories.director import DirectorRepository
from app.database.session import get_session
from app.schemas.common import DirectorBrief
from app.schemas.directors import DirectorBase, DirectorDetail, DirectorUpdate


class DirectorService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.directors = DirectorRepository(session)

    async def get_director_by_id(self, director_id: UUID) -> DirectorDetail:
        db_director = await self.directors.get_by_id_with_relations(director_id)

        if db_director is None:
            raise NotFoundError(detail=DirectorMessages.not_found(director_id=director_id)) from None

        director = DirectorDetail.model_validate(db_director)

        return director

    async def get_directors(self, name_search: str | None) -> list[DirectorBrief]:
        directors = await self.directors.get_directors(name_search)

        return directors

    async def create_director(self, payload: DirectorBase) -> DirectorBrief:
        db_director = Director(**payload.model_dump())

        try:
            await self.directors.save(db_director)
        except EntityAlreadyExistsError:
            raise AlreadyExistsError(detail=DirectorMessages.already_exists()) from None

        await self.session.commit()

        director = DirectorBrief.model_validate(db_director)

        return director

    async def update_director(self, director_id: UUID, payload: DirectorUpdate) -> DirectorBrief:
        db_director = await self.directors.get_by_id(director_id)

        if db_director is None:
            raise NotFoundError(detail=DirectorMessages.not_found(director_id=director_id)) from None

        director_data = payload.model_dump(exclude_unset=True)

        try:
            await self.directors.update(db_director, director_data)
        except EntityAlreadyExistsError:
            raise AlreadyExistsError(detail=DirectorMessages.already_exists()) from None

        await self.session.commit()

        director = DirectorBrief.model_validate(db_director)

        return director

    async def remove_director(self, director_id: UUID) -> None:
        try:
            await self.directors.delete(director_id)
        except EntityNotFoundError:
            raise NotFoundError(detail=DirectorMessages.not_found(director_id=director_id)) from None

        await self.session.commit()
