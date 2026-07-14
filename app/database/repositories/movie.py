from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions.repositories import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.database.models import Country, Director, Genre, Movie, Review
from app.schemas.common import CollectionEnvelope, DirectorBrief
from app.schemas.movies import CountryBase, GenreBase, MovieBrief, MovieSortBy

from .pg_error_codes import PostgresErrorCode as pg_err


class MovieRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _build_movie_brief_from_row(self, row: RowMapping) -> MovieBrief:
        return MovieBrief(
            id=row.id,
            title=row.title,
            release_year=row.release_year,
            rating=row.rating,
            director=DirectorBrief(
                id=row.director_id,
                first_name=row.director_first_name,
                last_name=row.director_last_name,
                date_of_birth=row.director_date_of_birth,
            ),
        )

    async def get_movies(
        self,
        country_ids: Sequence[int] | None,
        genre_ids: Sequence[int] | None,
        director_ids: Sequence[UUID] | None,
        sort_by: MovieSortBy,
        sort_desc: bool = False,
        limit: int = 10,
        offset: int = 0,
    ) -> CollectionEnvelope[MovieBrief]:
        query = select(
            Movie.id,
            Movie.title,
            Movie.release_year,
            Movie.rating,
            Movie.director_id,
            Director.first_name.label("director_first_name"),
            Director.last_name.label("director_last_name"),
            Director.date_of_birth.labe("director_date_of_birth"),
        ).join(Director, Director.id == Movie.director_id)

        if genre_ids:
            query = query.join(Movie.genres).where(Genre.id.in_(genre_ids))
        if country_ids:
            query = query.join(Movie.countries).where(Country.id.in_(country_ids))
        if director_ids:
            query = query.where(Director.id.in_(director_ids))

        query = query.group_by(Movie.id, Director.id)

        sort_column = getattr(Movie, sort_by.value)

        if sort_desc:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)

        rows = result.mappings().all()

        movies = [self._build_movie_brief_from_row(row) for row in rows]

        collection = CollectionEnvelope(
            items=movies,
            total=total,
        )

        return collection

    async def get_by_id(self, id: UUID) -> Movie | None:
        query = select(Movie).where(Movie.id == id)

        movie = await self.session.scalar(query)

        return movie

    async def get_by_id_with_relations(self, id: UUID) -> Movie | None:
        query = (
            select(Movie)
            .where(Movie.id == id)
            .options(
                selectinload(Movie.genres),
                selectinload(Movie.countries),
                selectinload(Movie.director),
            )
        )

        movie = await self.session.scalar(query)

        return movie

    async def update_rating(self, id: UUID) -> None:
        subquery = select(func.avg(Review.rating)).where(Review.movie_id == id).scalar_subquery()

        stmt = update(Movie).where(Movie.id == id).values(rating=subquery)

        await self.session.execute(stmt)

    async def save(
        self,
        movie: Movie,
    ) -> None:
        self.session.add(movie)

        try:
            await self.session.flush()
        except IntegrityError as e:
            sqlstate = getattr(e.orig, "sqlstate", None)

            if sqlstate == pg_err.UNIQUE_VIOLATION:
                raise EntityAlreadyExistsError from None

            if sqlstate == pg_err.FOREIGN_KEY_VIOLATION:
                raise EntityAlreadyExistsError from None

    async def update(self, movie: Movie, movie_data: Mapping[str, Any]) -> None:
        for key, value in movie_data.items():
            setattr(movie, key, value)

        try:
            await self.session.flush()
        except IntegrityError as e:
            sqlstate = getattr(e.orig, "sqlstate", None)

            if sqlstate == pg_err.UNIQUE_VIOLATION:
                raise EntityAlreadyExistsError from None

    async def delete_movie(self, id: UUID) -> None:
        stmt = delete(Movie).where(Movie.id == id).returning(Movie.id)

        result = await self.session.execute(stmt)

        if not result.scalar():
            raise EntityNotFoundError from None

    async def get_countries_by_id(self, countries_ids: Sequence[int]) -> Sequence[Country]:
        query = select(Country).where(Country.id.in_(countries_ids))

        result = await self.session.scalars(query)

        return result.all()

    async def get_genres_by_id(self, genres_ids: Sequence[int]) -> Sequence[Genre]:
        query = select(Genre).where(Genre.id.in_(genres_ids))

        result = await self.session.scalars(query)

        return result.all()

    async def get_all_genres(self) -> list[GenreBase]:
        result = await self.session.execute(select(Genre.id, Genre.name))

        rows = result.mappings().all()

        genres = [GenreBase.model_validate(row) for row in rows]

        return genres

    async def get_all_countries(self) -> list[CountryBase]:
        result = await self.session.execute(select(Country.id, Country.name))

        rows = result.mappings().all()

        countries = [CountryBase.model_validate(row) for row in rows]

        return countries
