from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Security, status

from app.schemas.common import CollectionEnvelope, ResponseEnvelope
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
from app.schemas.pagination import PaginationParams
from app.services.movies import MovieService

from .dependencies import IPBasedLimiter, RoleBasedLimiter, verify_global_permissions

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get(
    "/genres",
    response_model=ResponseEnvelope[list[GenreBase]],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_genres(
    request: Request,
    movie_service: MovieService = Depends(),
) -> ResponseEnvelope:
    genres = await movie_service.get_all_genres()

    return ResponseEnvelope(data=genres)


@router.get(
    "/countries",
    response_model=ResponseEnvelope[list[CountryBase]],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_countries(
    request: Request,
    movie_service: MovieService = Depends(),
) -> ResponseEnvelope:
    countries = await movie_service.get_all_countries()

    return ResponseEnvelope(data=countries)


@router.get(
    "",
    response_model=ResponseEnvelope[CollectionEnvelope[MovieBrief]],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_movies(
    request: Request,
    country_ids: Sequence[int] | None = Query(default=None),
    genre_ids: Sequence[int] | None = Query(default=None),
    director_ids: Sequence[UUID] | None = Query(default=None),
    sort: MovieSortCriteria = Depends(),
    movie_service: MovieService = Depends(),
    pagination: PaginationParams = Depends(),
) -> ResponseEnvelope:
    filters = MovieFilterCriteria(
        country_ids=country_ids,
        genre_ids=genre_ids,
        director_ids=director_ids,
    )

    movie_collection = await movie_service.get_movies(
        filters=filters,
        sort=sort,
        pagination=pagination,
    )

    movie_collection.limit = pagination.limit
    movie_collection.offset = pagination.offset

    return ResponseEnvelope(data=movie_collection)


@router.get(
    "/{movie_id}",
    response_model=ResponseEnvelope[MovieDetail],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_movie(
    request: Request,
    movie_id: UUID,
    movie_service: MovieService = Depends(),
) -> ResponseEnvelope:
    movie = await movie_service.get_movie_by_id(movie_id)

    return ResponseEnvelope(data=movie)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseEnvelope[MovieDetail],
    dependencies=[Depends(RoleBasedLimiter)],
)
async def post_movie(
    request: Request,
    movie_data: MoviePayload,
    user_id: UUID = Security(verify_global_permissions, scopes=["movies:post"]),
    movie_service: MovieService = Depends(),
) -> ResponseEnvelope:
    movie = await movie_service.create_movie(movie_data)

    return ResponseEnvelope(data=movie)


@router.patch(
    "/{movie_id}",
    response_model=ResponseEnvelope[MovieDetail],
    dependencies=[Depends(RoleBasedLimiter)],
)
async def patch_movie(
    request: Request,
    movie_id: UUID,
    movie_data: MovieUpdate,
    user_id: UUID = Security(verify_global_permissions, scopes=["movies:manage"]),
    movie_service: MovieService = Depends(),
) -> ResponseEnvelope:
    movie = await movie_service.update_movie(movie_id, movie_data)

    return ResponseEnvelope(data=movie)


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def delete_movie(
    request: Request,
    movie_id: UUID,
    user_id: UUID = Security(verify_global_permissions, scopes=["movies:delete"]),
    movie_service: MovieService = Depends(),
) -> None:
    await movie_service.remove_movie(movie_id)
