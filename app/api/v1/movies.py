from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Security, status

from app.schemas.common import CollectionEnvelope, PaginationParams, ResponseEnvelope
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
from app.services.movies.service import MovieService

from .dependencies import IPBasedLimiter, RoleBasedLimiter, verify_global_permissions
from .openapi import errors_model

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get(
    "",
    name="search_movies",
    summary="Search movies",
    description="""Searches movies using the provided filters.

All filters are optional and combined using logical AND.
Supports pagination with `limit` and `offset`.""",
    response_model=ResponseEnvelope[CollectionEnvelope[MovieBrief]],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 422, 429),
)
async def get_movies(
    request: Request,
    search: str | None = Query(default=None, max_length=100),
    country_ids: Sequence[int] | None = Query(default=None, max_length=20),
    genre_ids: Sequence[int] | None = Query(default=None, max_length=20),
    director_ids: Sequence[UUID] | None = Query(default=None, max_length=20),
    sort: MovieSortCriteria = Depends(),
    service: MovieService = Depends(),
    pagination: PaginationParams = Depends(),
) -> ResponseEnvelope:
    filters = MovieFilterCriteria(
        search=search,
        country_ids=country_ids,
        genre_ids=genre_ids,
        director_ids=director_ids,
    )

    movie_collection = await service.get_movies(
        filters=filters,
        sort=sort,
        pagination=pagination,
    )

    movie_collection.limit = pagination.limit
    movie_collection.offset = pagination.offset

    return ResponseEnvelope(data=movie_collection)


@router.get(
    "/genres",
    summary="List genres",
    response_model=ResponseEnvelope[CollectionEnvelope[GenreBase]],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 429),
)
async def get_genres(
    request: Request,
    pagination: PaginationParams = Depends(),
    service: MovieService = Depends(),
) -> ResponseEnvelope:
    genre_collection = await service.get_all_genres(pagination)

    return ResponseEnvelope(data=genre_collection)


@router.get(
    "/countries",
    summary="List countries",
    response_model=ResponseEnvelope[CollectionEnvelope[CountryBase]],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 429),
)
async def get_countries(
    request: Request,
    pagination: PaginationParams = Depends(),
    service: MovieService = Depends(),
) -> ResponseEnvelope:
    country_collection = await service.get_all_countries(pagination)

    return ResponseEnvelope(data=country_collection)


@router.post(
    "",
    name="create_movie",
    summary="Create a movie",
    description="Only administrators can perform this operation.",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseEnvelope[MovieDetail],
    dependencies=[Depends(RoleBasedLimiter)],
    responses=errors_model(400, 401, 403, 404, 409, 422, 429),
)
async def post_movie(
    request: Request,
    payload: MoviePayload,
    user_id: UUID = Security(verify_global_permissions, scopes=["movies:create"]),
    service: MovieService = Depends(),
) -> ResponseEnvelope:
    movie = await service.create_movie(payload)

    return ResponseEnvelope(data=movie)


@router.get(
    "/{movie_id}",
    summary="Get movie by ID",
    response_model=ResponseEnvelope[MovieDetail],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 404, 422, 429),
)
async def get_movie(
    request: Request,
    movie_id: UUID,
    service: MovieService = Depends(),
) -> ResponseEnvelope:
    movie = await service.get_movie_by_id(movie_id)

    return ResponseEnvelope(data=movie)


@router.patch(
    "/{movie_id}",
    summary="Update a movie",
    description="Only administrators can perform this operation.",
    response_model=ResponseEnvelope[MovieDetail],
    dependencies=[Depends(RoleBasedLimiter)],
    responses=errors_model(400, 401, 403, 404, 409, 422, 429),
)
async def patch_movie(
    request: Request,
    movie_id: UUID,
    payload: MovieUpdate,
    user_id: UUID = Security(verify_global_permissions, scopes=["movies:update"]),
    service: MovieService = Depends(),
) -> ResponseEnvelope:
    movie = await service.update_movie(movie_id, payload)

    return ResponseEnvelope(data=movie)


@router.delete(
    "/{movie_id}",
    name="delete_movie",
    summary="Delete a movie",
    description="Only administrators can perform this operation.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleBasedLimiter)],
    responses=errors_model(400, 401, 403, 404, 422, 429),
)
async def delete_movie(
    request: Request,
    movie_id: UUID,
    user_id: UUID = Security(verify_global_permissions, scopes=["movies:delete"]),
    service: MovieService = Depends(),
) -> None:
    await service.remove_movie(movie_id)
