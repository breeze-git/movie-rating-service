import logging
from collections.abc import Sequence
from uuid import UUID

from fastapi import Depends

from app.core.exceptions.repository import RepoUniqueViolationError
from app.database.models import Country, Genre, Movie
from app.database.uow import UnitOfWork
from app.schemas.common import CollectionEnvelope, PaginationParams
from app.schemas.movies import (
    CountryBase,
    GenreBase,
    MovieBrief,
    MovieDetail,
    MovieFilterCriteria,
    MoviePayload,
    MovieSortCriteria,
    MovieUpdate,
)
from app.services.directors.exceptions import DirectorNotFoundError
from app.services.movies.exceptions import (
    CountriesNotFoundError,
    GenresNotFoundError,
    MovieAlreadyExistsError,
    MovieNotFoundError,
)

logger = logging.getLogger(__name__)


class MovieService:
    def __init__(self, uow: UnitOfWork = Depends()):
        self.uow = uow

    async def _get_validated_countries(self, country_ids: Sequence[int]) -> Sequence[Country]:
        async with self.uow:
            if not country_ids:
                return []

            countries = await self.uow.movies.get_countries_by_id(country_ids)

            if len(countries) < len(country_ids):
                raise CountriesNotFoundError(country_ids) from None

            return countries

    async def _get_validated_genres(self, genre_ids: Sequence[int]) -> Sequence[Genre]:
        async with self.uow:
            if not genre_ids:
                return []

            genres = await self.uow.movies.get_genres_by_id(genre_ids)

            if len(genres) < len(genre_ids):
                raise GenresNotFoundError(genre_ids) from None

            return genres

    async def get_movies(
        self,
        filters: MovieFilterCriteria,
        sort: MovieSortCriteria,
        pagination: PaginationParams,
    ) -> CollectionEnvelope[MovieBrief]:
        async with self.uow:
            movie_collection = await self.uow.movies.get_movies(
                **filters.model_dump(),
                **sort.model_dump(),
                **pagination.model_dump(),
            )

            return movie_collection

    async def get_movie_by_id(self, movie_id: UUID) -> MovieDetail:
        async with self.uow:
            db_movie = await self.uow.movies.get_by_id_with_relations(movie_id)

            if db_movie is None:
                raise MovieNotFoundError(movie_id) from None

            movie = MovieDetail.model_validate(db_movie)

            return movie

    async def create_movie(self, dto: MoviePayload) -> MovieDetail:
        async with self.uow:
            db_director = await self.uow.directors.get_by_id(dto.director_id)

            if not db_director:
                raise DirectorNotFoundError(dto.director_id) from None

            genres = await self._get_validated_genres(dto.genre_ids)
            countries = await self._get_validated_countries(dto.country_ids)

            db_movie = Movie(
                **dto.model_dump(exclude={"country_ids", "genre_ids"}),
                genres=genres,
                countries=countries,
                director=db_director,
            )

            try:
                await self.uow.movies.save(db_movie)
            except RepoUniqueViolationError as e:
                raise MovieAlreadyExistsError(
                    conflict_value=dto.model_dump(include={"title", "release_year", "director_id"})
                ) from e

            movie = MovieDetail.model_validate(db_movie)

            logger.info(
                "Movie created",
                extra={"id": movie.id},
            )

            return movie

    async def update_movie(self, movie_id: UUID, dto: MovieUpdate) -> MovieDetail:
        async with self.uow:
            db_movie = await self.uow.movies.get_by_id_with_relations(movie_id)

            if db_movie is None:
                raise MovieNotFoundError(movie_id) from None

            if dto.director_id:
                if not await self.uow.directors.exists_by_id(dto.director_id):
                    raise DirectorNotFoundError(dto.director_id)

            genres = countries = None

            if dto.country_ids:
                countries = await self._get_validated_countries(dto.country_ids)

            if dto.genre_ids:
                genres = await self._get_validated_genres(dto.genre_ids)

            update_data = dto.model_dump(exclude_unset=True, exclude={"country_ids", "genre_ids"})

            try:
                await self.uow.movies.update(db_movie, update_data, genres=genres, countries=countries)
            except RepoUniqueViolationError as e:
                raise MovieAlreadyExistsError(
                    conflict_value=dto.model_dump(include={"title", "release_year", "director_id"})
                ) from e

            movie = MovieDetail.model_validate(db_movie)

            return movie

    async def remove_movie(self, movie_id: UUID) -> None:
        async with self.uow:
            result = await self.uow.movies.delete(movie_id)

            if not result.scalar():
                raise MovieNotFoundError(movie_id) from None

            logger.info(
                "Movie deleted",
                extra={"id": movie_id},
            )

    async def get_all_genres(self, pagination: PaginationParams) -> CollectionEnvelope[GenreBase]:
        async with self.uow:
            genre_collection = await self.uow.movies.get_all_genres(limit=pagination.limit, offset=pagination.offset)

            return genre_collection

    async def get_all_countries(self, pagination: PaginationParams) -> CollectionEnvelope[CountryBase]:
        async with self.uow:
            country_collection = await self.uow.movies.get_all_countries(
                limit=pagination.limit, offset=pagination.offset
            )

            return country_collection
