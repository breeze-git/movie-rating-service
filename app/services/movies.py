from collections.abc import Sequence
from uuid import UUID, uuid4

from fastapi import Depends
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.error_messages import MovieMessages
from app.core.exceptions.repositories import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from app.core.exceptions.services import AlreadyExistsError, NotFoundError
from app.database.models import Country, Genre, Movie
from app.database.repositories.movie import MovieRepository
from app.database.session import get_session
from app.schemas.movies import (
    MovieAddRequest,
    MovieDTO,
    MovieFilter,
    MoviePatchRequest,
    MovieSort,
    PaginatedMovieDTO,
)
from app.schemas.pagination import PaginationParams


class MovieService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.movies = MovieRepository(session)

    async def _get_validated_countries(self, countries_ids: list[int]) -> Sequence[Country]:
        if not countries_ids:
            return []

        countries = await self.movies.get_countries_by_id(countries_ids)

        if len(countries) < len(countries_ids):
            raise NotFoundError(detail=MovieMessages.countries_not_found()) from None

        return countries

    async def _get_validated_genres(self, genres_ids: list[int]) -> Sequence[Genre]:
        if not genres_ids:
            return []

        genres = await self.movies.get_genres_by_id(genres_ids)

        if len(genres) < len(genres_ids):
            raise NotFoundError(detail=MovieMessages.genres_not_found()) from None

        return genres

    async def get_movies(
        self,
        filters: MovieFilter,
        sort: MovieSort,
        pagination: PaginationParams,
    ) -> PaginatedMovieDTO:
        movies, total = await self.movies.get_movies(
            **filters.model_dump(),
            **sort.model_dump(),
            **pagination.model_dump(),
        )

        movie_dtos = [MovieDTO.model_validate(row) for row in movies]

        return PaginatedMovieDTO(items=movie_dtos, total=total)

    async def get_movie_by_id(self, movie_id: UUID):
        movie = await self.movies.get_by_id_with_relations(movie_id)

        if movie is None:
            raise NotFoundError(detail=MovieMessages.not_found(movie_id=movie_id)) from None

        return movie

    async def post_movie(self, movie_data: MovieAddRequest) -> UUID:
        id = uuid4()

        countries = await self._get_validated_countries(movie_data.countries)
        genres = await self._get_validated_genres(movie_data.genres)

        movie = Movie(
            id=id,
            director_id=movie_data.director_id,
            title=movie_data.title,
            description=movie_data.description,
            release_year=movie_data.release_year,
            countries=countries,
            genres=genres,
        )

        try:
            await self.movies.save(movie)
        except EntityAlreadyExistsError:
            raise AlreadyExistsError(detail=MovieMessages.already_exists()) from None

        await self.session.commit()

        return id

    async def update_movie(self, movie_id: UUID, movie_data: MovieAddRequest) -> None:
        movie = await self.movies.get_by_id_with_relations(movie_id)

        if movie is None:
            raise NotFoundError(detail=MovieMessages.not_found(movie_id=movie_id)) from None

        countries = await self._get_validated_countries(movie_data.countries)
        genres = await self._get_validated_genres(movie_data.genres)

        movie_data_dict = movie_data.model_dump()

        movie_data_dict["countries"] = countries
        movie_data_dict["genres"] = genres

        try:
            await self.movies.update(movie, movie_data_dict)
        except EntityAlreadyExistsError:
            raise AlreadyExistsError(detail=MovieMessages.already_exists()) from None

        await self.session.commit()

    async def partial_update_movie(self, movie_id: UUID, movie_data: MoviePatchRequest) -> None:
        if movie_data.countries or movie_data.genres:
            movie = await self.movies.get_by_id_with_relations(movie_id)
        else:
            movie = await self.movies.get_by_id(movie_id)

        if movie is None:
            raise NotFoundError(detail=MovieMessages.not_found(movie_id=movie_id)) from None

        movie_data_dict = movie_data.model_dump(exclude_unset=True)

        if movie_data.countries:
            movie_data_dict["countries"] = await self._get_validated_countries(
                movie_data.countries,
            )
        if movie_data.genres:
            movie_data_dict["genres"] = await self._get_validated_genres(
                movie_data.genres,
            )

        try:
            await self.movies.update(movie, movie_data_dict)
        except EntityAlreadyExistsError:
            raise AlreadyExistsError(detail=MovieMessages.already_exists()) from None

        await self.session.commit()

    async def remove_movie(self, movie_id: UUID):
        try:
            await self.movies.delete_movie(movie_id)
        except EntityNotFoundError:
            raise NotFoundError(detail=MovieMessages.not_found(movie_id=movie_id)) from None

        await self.session.commit()

    async def get_all_genres(self) -> Sequence[RowMapping]:
        genres = await self.movies.get_all_genres()

        return genres

    async def get_all_countries(self) -> Sequence[RowMapping]:
        countries = await self.movies.get_all_countries()

        return countries
