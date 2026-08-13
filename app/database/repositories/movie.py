from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.orm import selectinload

from app.database.models import Country, Director, Genre, Movie, Review
from app.schemas.common import CollectionEnvelope, DirectorBrief
from app.schemas.movies import CountryBase, GenreBase, MovieBrief, MovieSortBy

from .base import BaseRepository


class MovieRepository(BaseRepository):
    model = Movie

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
        search: str | None = None,
        country_ids: Sequence[int] | None = None,
        genre_ids: Sequence[int] | None = None,
        director_ids: Sequence[UUID] | None = None,
        sort_by: MovieSortBy = MovieSortBy.RELEASE_YEAR,
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
            Director.date_of_birth.label("director_date_of_birth"),
        ).join(Director, Director.id == Movie.director_id)

        if search:
            query = query.where(
                or_(
                    Movie.title.ilike(f"%{search}%"),
                    func.concat(Director.first_name, " ", Director.last_name).ilike(f"%{search}%"),
                )
            )
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
            limit=limit,
            offset=offset,
        )

        return collection

    async def get_by_id_with_relations(self, movie_id: UUID) -> Movie | None:
        query = (
            select(Movie)
            .where(Movie.id == movie_id)
            .options(
                selectinload(Movie.genres),
                selectinload(Movie.countries),
                selectinload(Movie.director),
            )
        )

        result = await self._execute(query)

        movie = result.scalar()

        return movie

    async def update_rating(self, movie_id: UUID) -> None:
        subquery = select(func.avg(Review.rating)).where(Review.movie_id == movie_id).scalar_subquery()

        stmt = update(Movie).where(Movie.id == movie_id).values(rating=subquery)

        await self._execute(stmt)

    async def update(
        self,
        movie: Movie,
        update_data: Mapping[str, Any],
        genres: Sequence[Genre] | None = None,
        countries: Sequence[Country] | None = None,
    ) -> None:
        for key, value in update_data.items():
            setattr(movie, key, value)

        if genres is not None:
            movie.genres = list(genres)

        if countries is not None:
            movie.countries = list(countries)

        await self._flush()

    async def get_countries_by_id(self, country_ids: Sequence[int]) -> Sequence[Country]:
        query = select(Country).where(Country.id.in_(country_ids))

        result = await self.session.scalars(query)

        return result.all()

    async def get_genres_by_id(self, genre_ids: Sequence[int]) -> Sequence[Genre]:
        query = select(Genre).where(Genre.id.in_(genre_ids))

        result = await self.session.scalars(query)

        return result.all()

    async def get_all_genres(self) -> list[GenreBase]:
        query = select(Genre.id, Genre.name)

        result = await self.session.execute(query)

        rows = result.mappings().all()

        genres = [GenreBase.model_validate(row) for row in rows]

        return genres

    async def get_all_countries(self) -> list[CountryBase]:
        query = select(Country.id, Country.name)

        result = await self.session.execute(query)

        rows = result.mappings().all()

        countries = [CountryBase.model_validate(row) for row in rows]

        return countries
