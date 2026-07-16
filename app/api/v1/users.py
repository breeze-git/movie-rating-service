from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from app.schemas.common import ResponseEnvelope
from app.schemas.users import UserBrief, UserDetail, UserUpdate, UserWithReviews
from app.services.users import UserService

from .dependencies import IPBasedLimiter, RoleBasedLimiter, get_user_id_from_token

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=ResponseEnvelope[UserDetail],
    dependencies=[Depends(RoleBasedLimiter)],
)
async def get_profile(
    request: Request,
    user_id: UUID = Depends(get_user_id_from_token),
    service: UserService = Depends(),
) -> ResponseEnvelope:
    user = await service.get_profile(user_id)

    return ResponseEnvelope(data=user)


@router.get(
    "/{user_id}",
    response_model=ResponseEnvelope[UserWithReviews],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_user(
    request: Request,
    user_id: UUID,
    service: UserService = Depends(),
) -> ResponseEnvelope:
    user = await service.get_user(user_id)

    return ResponseEnvelope(data=user)


@router.patch(
    "/me",
    response_model=ResponseEnvelope[UserBrief],
    dependencies=[Depends(RoleBasedLimiter)],
)
async def patch_user(
    request: Request,
    payload: UserUpdate,
    user_id: UUID = Depends(get_user_id_from_token),
    service: UserService = Depends(),
) -> ResponseEnvelope:
    user = await service.update_user(user_id, payload)

    return ResponseEnvelope(data=user)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def delete_user(
    request: Request,
    user_id: UUID = Depends(get_user_id_from_token),
    service: UserService = Depends(),
) -> None:
    await service.remove_user(user_id)
