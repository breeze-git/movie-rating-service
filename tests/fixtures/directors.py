import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Director
from tests.factories.directors import DirectorBaseFactory


@pytest_asyncio.fixture
async def created_director(
    db_session: AsyncSession,
):
    director_payload = DirectorBaseFactory.build()

    db_director = Director(**director_payload.model_dump())

    db_session.add(db_director)

    await db_session.commit()

    return db_director
