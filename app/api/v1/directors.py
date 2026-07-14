from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Security, status

from app.schemas.common import DirectorBrief, ResponseEnvelope
from app.schemas.directors import DirectorBase, DirectorDetail, DirectorUpdate
from app.services.directors import DirectorService

from .dependencies import IPBasedLimiter, RoleBasedLimiter, verify_global_permissions

router = APIRouter(prefix="/directors", tags=["Directors"])


@router.get(
    "/search",
    response_model=ResponseEnvelope[list[DirectorBrief]],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_directors(
    request: Request,
    name_search: str | None = Query(default=None, description="Search director by fullname"),
    director_service: DirectorService = Depends(),
) -> ResponseEnvelope:
    directors = await director_service.get_directors(name_search)

    print("Hello")

    return ResponseEnvelope(data=directors)


@router.get(
    "/{director_id}",
    response_model=ResponseEnvelope[DirectorDetail],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_director(
    request: Request, director_id: UUID, director_service: DirectorService = Depends()
) -> ResponseEnvelope:
    director = await director_service.get_director_by_id(director_id)

    return ResponseEnvelope(data=director)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseEnvelope[DirectorBrief],
    dependencies=[Depends(RoleBasedLimiter)],
)
async def post_director(
    request: Request,
    director_data: DirectorBase,
    user_id: UUID = Security(verify_global_permissions, scopes=["directors:post"]),
    director_service: DirectorService = Depends(),
) -> ResponseEnvelope:
    director = await director_service.create_director(director_data)

    return ResponseEnvelope(data=director)


@router.patch(
    "/{director_id}",
    response_model=ResponseEnvelope[DirectorBrief],
    dependencies=[Depends(RoleBasedLimiter)],
)
async def patch_director(
    request: Request,
    director_id: UUID,
    director_data: DirectorUpdate,
    user_id: UUID = Security(verify_global_permissions, scopes=["directors:manage"]),
    director_service: DirectorService = Depends(),
) -> ResponseEnvelope:
    director = await director_service.update_director(director_id, director_data)

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
    director_service: DirectorService = Depends(),
) -> None:
    await director_service.remove_director(director_id)
