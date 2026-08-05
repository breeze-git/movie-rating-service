from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Security, status

from app.schemas.common import (
    CollectionEnvelope,
    DirectorBrief,
    PaginationParams,
    ResponseEnvelope,
)
from app.schemas.directors import DirectorBase, DirectorDetail, DirectorUpdate
from app.services.directors.service import DirectorService

from .dependencies import IPBasedLimiter, RoleBasedLimiter, verify_global_permissions
from .openapi import errors_model

router = APIRouter(prefix="/directors", tags=["Directors"])


@router.get(
    "",
    summary="Search directors",
    response_model=ResponseEnvelope[CollectionEnvelope[DirectorBrief]],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 422, 429),
)
async def get_directors(
    request: Request,
    search: str | None = Query(default=None, max_length=100, description="Search director by fullname"),
    pagination: PaginationParams = Depends(),
    service: DirectorService = Depends(),
) -> ResponseEnvelope:
    director_collection = await service.get_directors(
        search=search,
        pagination=pagination,
    )

    return ResponseEnvelope(data=director_collection)


@router.post(
    "",
    summary="Create a director",
    description="Only administrators can perform this operation.",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseEnvelope[DirectorBrief],
    dependencies=[Depends(RoleBasedLimiter)],
    responses=errors_model(400, 401, 403, 409, 422, 429),
)
async def post_director(
    request: Request,
    payload: DirectorBase,
    user_id: UUID = Security(verify_global_permissions, scopes=["directors:create"]),
    service: DirectorService = Depends(),
) -> ResponseEnvelope:
    director = await service.create_director(payload)

    return ResponseEnvelope(data=director)


@router.get(
    "/{director_id}",
    summary="Get director by ID",
    response_model=ResponseEnvelope[DirectorDetail],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 404, 422, 429),
)
async def get_director(request: Request, director_id: UUID, service: DirectorService = Depends()) -> ResponseEnvelope:
    director = await service.get_director_by_id(director_id)

    return ResponseEnvelope(data=director)


@router.patch(
    "/{director_id}",
    summary="Update a director",
    description="Only administrators can perform this operation.",
    response_model=ResponseEnvelope[DirectorBrief],
    dependencies=[Depends(RoleBasedLimiter)],
    responses=errors_model(400, 401, 403, 404, 409, 422, 429),
)
async def patch_director(
    request: Request,
    director_id: UUID,
    payload: DirectorUpdate,
    user_id: UUID = Security(verify_global_permissions, scopes=["directors:update"]),
    service: DirectorService = Depends(),
) -> ResponseEnvelope:
    director = await service.update_director(director_id, payload)

    return ResponseEnvelope(data=director)


@router.delete(
    "/{director_id}",
    summary="Delete a director",
    description="Only administrators can perform this operation.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleBasedLimiter)],
    responses=errors_model(400, 401, 403, 404, 422, 429),
)
async def delete_director(
    request: Request,
    director_id: UUID,
    user_id: UUID = Security(verify_global_permissions, scopes=["directors:delete"]),
    service: DirectorService = Depends(),
) -> None:
    await service.remove_director(director_id)
