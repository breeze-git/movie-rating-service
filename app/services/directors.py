from uuid import UUID, uuid4

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
from app.schemas.directors import DirectorAddRequest, DirectorPatchRequest


class DirectorService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.directors = DirectorRepository(session)

    async def get_director_by_id(self, director_id: UUID) -> Director:
        director = await self.directors.get_by_id_with_relations(director_id)

        if director is None:
            raise NotFoundError(detail=DirectorMessages.not_found(director_id=director_id)) from None

        return director

    async def get_directors(self, name_search: str | None):
        directors = await self.directors.get_directors(name_search)

        return directors

    async def create_director(self, director_data: DirectorAddRequest) -> UUID:
        director_id = uuid4()

        director = Director(
            id=director_id,
            first_name=director_data.first_name,
            last_name=director_data.last_name,
            date_of_birth=director_data.date_of_birth,
        )

        try:
            await self.directors.save(director)
        except EntityAlreadyExistsError:
            raise AlreadyExistsError(detail=DirectorMessages.already_exists()) from None

        await self.session.commit()

        return director_id

    async def update_director(self, director_id: UUID, director_data: DirectorAddRequest):
        director = await self.directors.get_by_id(director_id)

        if director is None:
            raise NotFoundError(detail=DirectorMessages.not_found(director_id=director_id)) from None

        director_data_dict = director_data.model_dump()

        try:
            await self.directors.update(director, director_data_dict)
        except EntityAlreadyExistsError:
            raise AlreadyExistsError(detail=DirectorMessages.already_exists()) from None

        await self.session.commit()

    async def partial_update_director(self, director_id: UUID, director_data: DirectorPatchRequest) -> None:
        director = await self.directors.get_by_id(director_id)

        if director is None:
            raise NotFoundError(detail=DirectorMessages.not_found(director_id=director_id)) from None

        director_data_dict = director_data.model_dump(exclude_unset=True)

        try:
            await self.directors.update(director, director_data_dict)
        except EntityAlreadyExistsError:
            raise AlreadyExistsError(detail=DirectorMessages.already_exists()) from None

        await self.session.commit()

    async def remove_director(self, director_id: UUID):
        try:
            await self.directors.delete(director_id)
        except EntityNotFoundError:
            raise NotFoundError(detail=DirectorMessages.not_found(director_id=director_id)) from None

        await self.session.commit()
