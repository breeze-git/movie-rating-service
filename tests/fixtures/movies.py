import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Country, Director, Genre, Movie
from app.schemas.movies import MoviePayload
from tests.factories.movies import MoviePayloadFactory


@pytest.fixture
def movie_payload():
    return MoviePayloadFactory.build()


@pytest_asyncio.fixture
async def created_movie_payload(
    db_session: AsyncSession,
    movie_payload: MoviePayload,
    created_director: Director,
) -> MoviePayload:
    movie_payload.director_id = created_director.id

    countries_query = select(Country).where(Country.id.in_(movie_payload.country_ids))
    genres_query = select(Genre).where(Genre.id.in_(movie_payload.genre_ids))

    countries = (await db_session.scalars(countries_query)).all()
    genres = (await db_session.scalars(genres_query)).all()

    db_movie = Movie(
        **movie_payload.model_dump(exclude={"country_ids", "genre_ids"}),
        countries=countries,
        genres=genres,
    )

    db_session.add(db_movie)

    await db_session.commit()

    return movie_payload
