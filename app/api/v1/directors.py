from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Security, status

from app.schemas.directors import (
    DirectorAddRequest,
    DirectorAddResponse,
    DirectorDeleteResponse,
    DirectorGetResponse,
    DirectorManageResponse,
    DirectorPatchRequest,
    DirectorsSearchResponse,
)
from app.services.directors import DirectorService

from .dependencies import IPBasedLimiter, RoleBasedLimiter, verify_global_permissions

router = APIRouter(prefix="/directors", tags=["Directors"])


@router.get(
    "/{director_id}",
    response_model=DirectorGetResponse,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_director(
    request: Request, director_id: UUID, director_service: DirectorService = Depends()
) -> DirectorGetResponse:
    director = await director_service.get_director_by_id(director_id)

    return DirectorGetResponse.model_validate(director)


@router.get(
    "/search",
    response_model=DirectorsSearchResponse,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_directors(
    request: Request,
    name_search: str | None = Query(default=None, description="Search director by fullname"),
    director_service: DirectorService = Depends(),
) -> DirectorsSearchResponse:
    directors = await director_service.get_directors(name_search)

    return DirectorsSearchResponse.model_validate(directors)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=DirectorAddResponse,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def post_director(
    request: Request,
    director_data: DirectorAddRequest,
    user_id: UUID = Security(verify_global_permissions, scopes=["directors:post"]),
    director_service: DirectorService = Depends(),
):
    director_id = await director_service.create_director(director_data)

    return DirectorAddResponse(id=director_id)


@router.put(
    "/{director_id}",
    response_model=DirectorManageResponse,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def put_director(
    request: Request,
    director_id: UUID,
    director_data: DirectorAddRequest,
    user_id: UUID = Security(verify_global_permissions, scopes=["directors:manage"]),
    director_service: DirectorService = Depends(),
) -> DirectorManageResponse:
    await director_service.update_director(director_id, director_data)

    return DirectorManageResponse()


@router.patch(
    "/{director_id}",
    response_model=DirectorManageResponse,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def patch_director(
    request: Request,
    director_id: UUID,
    director_data: DirectorPatchRequest,
    user_id: UUID = Security(verify_global_permissions, scopes=["directors:manage"]),
    director_service: DirectorService = Depends(),
) -> DirectorManageResponse:
    await director_service.partial_update_director(director_id, director_data)

    return DirectorManageResponse()


@router.delete(
    "/{director_id}",
    response_model=DirectorDeleteResponse,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def delete_director(
    request: Request,
    director_id: UUID,
    user_id: UUID = Security(verify_global_permissions, scopes=["directors:delete"]),
    director_service: DirectorService = Depends(),
) -> DirectorDeleteResponse:
    await director_service.remove_director(director_id)

    return DirectorDeleteResponse()
