import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Director
from tests.factories.directors import DirectorBaseFactory
from tests.schemas import DirectorDTO


@pytest_asyncio.fixture
async def created_director_dto(
    db_session: AsyncSession,
) -> DirectorDTO:
    director_payload = DirectorBaseFactory.build()

    db_director = Director(**director_payload.model_dump())

    db_session.add(db_director)

    await db_session.flush()

    director = DirectorDTO.model_validate(db_director)

    return director
