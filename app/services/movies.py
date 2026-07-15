from collections.abc import Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.error_messages import DirectorMessages, MovieMessages
from app.core.exceptions.repositories import RepositoryException
from app.core.exceptions.services import NotFoundError
from app.database.models import Country, Genre, Movie
from app.database.repositories.director import DirectorRepository
from app.database.repositories.movie import MovieRepository
from app.database.session import get_session
from app.schemas.common import CollectionEnvelope
from app.schemas.movies import (
    CountryBase,
    GenreBase,
    MovieDetail,
    MovieFilterCriteria,
    MoviePayload,
    MovieSortCriteria,
    MovieUpdate,
)
from app.schemas.pagination import PaginationParams

from .base import BaseService
from .integrity_maps import MOVIE_INTEGRITY_MAP


class MovieService(BaseService):
    _integrity_map = MOVIE_INTEGRITY_MAP

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.movies = MovieRepository(session)
        self.directors = DirectorRepository(session)

        super().__init__(session)

    async def _get_validated_countries(self, country_ids: Sequence[int]) -> Sequence[Country]:
        if not country_ids:
            return []

        countries = await self.movies.get_countries_by_id(country_ids)

        if len(countries) < len(country_ids):
            raise NotFoundError(detail=MovieMessages.countries_not_found()) from None

        return countries

    async def _get_validated_genres(self, genre_ids: Sequence[int]) -> Sequence[Genre]:
        if not genre_ids:
            return []

        genres = await self.movies.get_genres_by_id(genre_ids)

        if len(genres) < len(genre_ids):
            raise NotFoundError(detail=MovieMessages.genres_not_found()) from None

        return genres

    async def get_movies(
        self,
        filters: MovieFilterCriteria,
        sort: MovieSortCriteria,
        pagination: PaginationParams,
    ) -> CollectionEnvelope:
        movie_collection = await self.movies.get_movies(
            **filters.model_dump(),
            **sort.model_dump(),
            **pagination.model_dump(),
        )

        return movie_collection

    async def get_movie_by_id(self, movie_id: UUID) -> MovieDetail:
        db_movie = await self.movies.get_by_id_with_relations(movie_id)

        if db_movie is None:
            raise NotFoundError(detail=MovieMessages.not_found(movie_id=movie_id)) from None

        movie = MovieDetail.model_validate(db_movie)

        return movie

    async def create_movie(self, payload: MoviePayload) -> MovieDetail:
        director = await self.directors.get_by_id(payload.director_id)

        if not director:
            raise NotFoundError(DirectorMessages.not_found(director_id=payload.director_id)) from None

        genres = await self._get_validated_genres(payload.genre_ids)
        countries = await self._get_validated_countries(payload.country_ids)

        db_movie = Movie(
            **payload.model_dump(exclude={"country_ids", "genre_ids"}),
            genres=genres,
            countries=countries,
            director=director,
        )

        try:
            await self.movies.save(db_movie)
        except RepositoryException as e:
            raise self._handle_repo_error(exc=e, **payload.model_dump()) from None

        await self.session.commit()

        movie = MovieDetail.model_validate(db_movie)

        return movie

    async def update_movie(self, movie_id: UUID, payload: MovieUpdate) -> MovieDetail:
        db_movie = await self.movies.get_by_id_with_relations(movie_id)

        if db_movie is None:
            raise NotFoundError(detail=MovieMessages.not_found(movie_id=movie_id)) from None

        genres = countries = None

        if payload.country_ids:
            countries = await self._get_validated_countries(payload.country_ids)

        if payload.genre_ids:
            genres = await self._get_validated_genres(payload.genre_ids)

        movie_data = payload.model_dump(exclude_unset=True, exclude={"country_ids", "genre_ids"})

        try:
            await self.movies.update(
                db_movie,
                movie_data,
                genres=genres,
                countries=countries,
            )
        except RepositoryException as e:
            raise self._handle_repo_error(exc=e, movie_id=movie_id, **payload.model_dump()) from None

        await self.session.commit()

        movie = MovieDetail.model_validate(db_movie)

        return movie

    async def remove_movie(self, movie_id: UUID) -> None:
        result = await self.movies.delete(movie_id)

        if not result.scalar():
            raise NotFoundError(detail=MovieMessages.not_found(movie_id=movie_id)) from None

        await self.session.commit()

    async def get_all_genres(self) -> list[GenreBase]:
        genres = await self.movies.get_all_genres()

        return genres

    async def get_all_countries(self) -> list[CountryBase]:
        countries = await self.movies.get_all_countries()

        return countries
