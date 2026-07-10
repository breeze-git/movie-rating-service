from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Security, status

from app.schemas.movies import (
    CountriesGetResponse,
    GenresGetResponse,
    MovieAddRequest,
    MovieAddResponse,
    MovieDeleteResponse,
    MovieFilter,
    MovieGetResponse,
    MovieManageResponse,
    MoviePatchRequest,
    MovieSort,
    PaginatedMovieDTO,
)
from app.schemas.pagination import PaginationParams
from app.services.movies import MovieService

from .dependencies import IPBasedLimiter, RoleBasedLimiter, verify_global_permissions

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get(
    "/genres",
    response_model=GenresGetResponse,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_genres(
    request: Request,
    movie_service: MovieService = Depends(),
) -> GenresGetResponse:
    genres = await movie_service.get_all_genres()

    return GenresGetResponse.model_validate(genres)


@router.get(
    "/countries",
    response_model=CountriesGetResponse,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_countries(
    request: Request,
    movie_service: MovieService = Depends(),
) -> CountriesGetResponse:
    countries = await movie_service.get_all_countries()

    return CountriesGetResponse.model_validate(countries)


@router.get(
    "",
    response_model=PaginatedMovieDTO,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_movies(
    request: Request,
    countries: Sequence[int] | None = Query(default=None),
    genres: Sequence[int] | None = Query(default=None),
    directors: Sequence[UUID] | None = Query(default=None),
    sort: MovieSort = Depends(),
    movie_service: MovieService = Depends(),
    pagination: PaginationParams = Depends(),
) -> PaginatedMovieDTO:
    filters = MovieFilter(
        countries=countries,
        genres=genres,
        directors=directors,
    )

    paginated_movies = await movie_service.get_movies(
        filters=filters,
        sort=sort,
        pagination=pagination,
    )

    paginated_movies.limit = pagination.limit
    paginated_movies.offset = pagination.offset

    return paginated_movies


@router.get(
    "/{movie_id}",
    response_model=MovieGetResponse,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_movie(
    request: Request,
    movie_id: UUID,
    movie_service: MovieService = Depends(),
):
    movie = await movie_service.get_movie_by_id(movie_id)

    return MovieGetResponse.model_validate(movie)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=MovieAddResponse,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def post_movie(
    request: Request,
    movie_data: MovieAddRequest,
    user_id: UUID = Security(verify_global_permissions, scopes=["movies:post"]),
    movie_service: MovieService = Depends(),
) -> MovieAddResponse:
    movie_id = await movie_service.post_movie(movie_data)

    return MovieAddResponse(id=movie_id)


@router.put(
    "/{movie_id}",
    response_model=MovieManageResponse,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def put_movie(
    request: Request,
    movie_id: UUID,
    movie_data: MovieAddRequest,
    user_id: UUID = Security(verify_global_permissions, scopes=["movies:manage"]),
    movie_service: MovieService = Depends(),
) -> MovieManageResponse:
    await movie_service.update_movie(movie_id, movie_data)

    return MovieManageResponse()


@router.patch(
    "/{movie_id}",
    response_model=MovieManageResponse,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def patch_movie(
    request: Request,
    movie_id: UUID,
    movie_data: MoviePatchRequest,
    user_id: UUID = Security(verify_global_permissions, scopes=["movies:manage"]),
    movie_service: MovieService = Depends(),
) -> MovieManageResponse:
    await movie_service.partial_update_movie(movie_id, movie_data)

    return MovieManageResponse()


@router.delete(
    "/{movie_id}",
    response_model=MovieDeleteResponse,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def delete_movie(
    request: Request,
    movie_id: UUID,
    user_id: UUID = Security(verify_global_permissions, scopes=["movies:delete"]),
    movie_service: MovieService = Depends(),
) -> MovieDeleteResponse:
    await movie_service.remove_movie(movie_id)

    return MovieDeleteResponse()
