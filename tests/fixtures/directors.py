import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Director
from app.schemas.directors import DirectorBase
from tests.factories.directors import DirectorBaseFactory


@pytest.fixture
def director_payload():
    return DirectorBaseFactory.build()


@pytest_asyncio.fixture
async def created_director(
    db_session: AsyncSession,
    director_payload: DirectorBase,
):
    db_director = Director(**director_payload.model_dump())

    db_session.add(db_director)

    await db_session.commit()

    return db_director
