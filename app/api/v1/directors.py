from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Security, status

from app.schemas.common import CollectionEnvelope, DirectorBrief, ResponseEnvelope
from app.schemas.directors import DirectorBase, DirectorDetail, DirectorUpdate
from app.schemas.pagination import PaginationParams
from app.services.directors import DirectorService

from .dependencies import IPBasedLimiter, RoleBasedLimiter, verify_global_permissions

router = APIRouter(prefix="/directors", tags=["Directors"])


@router.get(
    "",
    response_model=ResponseEnvelope[CollectionEnvelope[DirectorBrief]],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_directors(
    request: Request,
    search: str | None = Query(default=None, description="Search director by fullname"),
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
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseEnvelope[DirectorBrief],
    dependencies=[Depends(RoleBasedLimiter)],
)
async def post_director(
    request: Request,
    payload: DirectorBase,
    user_id: UUID = Security(verify_global_permissions, scopes=["directors:post"]),
    service: DirectorService = Depends(),
) -> ResponseEnvelope:
    director = await service.create_director(payload)

    return ResponseEnvelope(data=director)


@router.get(
    "/{director_id}",
    response_model=ResponseEnvelope[DirectorDetail],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_director(request: Request, director_id: UUID, service: DirectorService = Depends()) -> ResponseEnvelope:
    director = await service.get_director_by_id(director_id)

    return ResponseEnvelope(data=director)


@router.patch(
    "/{director_id}",
    response_model=ResponseEnvelope[DirectorBrief],
    dependencies=[Depends(RoleBasedLimiter)],
)
async def patch_director(
    request: Request,
    director_id: UUID,
    payload: DirectorUpdate,
    user_id: UUID = Security(verify_global_permissions, scopes=["directors:manage"]),
    service: DirectorService = Depends(),
) -> ResponseEnvelope:
    director = await service.update_director(director_id, payload)

    return ResponseEnvelope(data=director)


@router.delete(
    "/{director_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def delete_director(
    request: Request,
    director_id: UUID,
    user_id: UUID = Security(verify_global_permissions, scopes=["directors:delete"]),
    service: DirectorService = Depends(),
) -> None:
    await service.remove_director(director_id)
