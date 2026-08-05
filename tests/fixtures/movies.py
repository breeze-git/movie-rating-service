from collections.abc import Callable

import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Country, Director, Genre, Movie
from app.schemas.movies import MoviePayload
from tests.factories.movies import MoviePayloadFactory


@pytest_asyncio.fixture
async def create_movie_in_db(db_session: AsyncSession) -> Callable:
    async def _create_movie(payload: MoviePayload) -> Movie:
        countries_query = select(Country).where(Country.id.in_(payload.country_ids))
        genres_query = select(Genre).where(Genre.id.in_(payload.genre_ids))

        countries = (await db_session.scalars(countries_query)).all()
        genres = (await db_session.scalars(genres_query)).all()

        db_movie = Movie(
            **payload.model_dump(exclude={"country_ids", "genre_ids"}),
            countries=countries,
            genres=genres,
        )

        db_session.add(db_movie)

        await db_session.commit()

        return db_movie

    return _create_movie


@pytest_asyncio.fixture
async def created_movie_payload(
    created_director: Director,
    create_movie_in_db: Callable,
) -> MoviePayload:
    movie_payload = MoviePayloadFactory.build()
    movie_payload.director_id = created_director.id

    await create_movie_in_db(movie_payload)

    return movie_payload


@pytest_asyncio.fixture
async def created_movie(
    created_director: Director,
    create_movie_in_db: Callable,
) -> Movie:
    movie_payload = MoviePayloadFactory.build()
    movie_payload.director_id = created_director.id

    db_movie = await create_movie_in_db(movie_payload)

    return db_movie
