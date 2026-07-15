from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.schemas.users import (
    UserDeleteResponse,
    UserGetResponse,
    UserPatchRequest,
    UserProfileResponse,
    UserUpdateResponse,
)
from app.services.users import UserService

from .dependencies import IPBasedLimiter, RoleBasedLimiter, get_user_id_from_token

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserProfileResponse,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def get_profile(
    request: Request,
    user_id: UUID = Depends(get_user_id_from_token),
    user_service: UserService = Depends(),
):
    user = await user_service.get_user(user_id)

    return UserProfileResponse.model_validate(user)


@router.get(
    "/{user_id}",
    response_model=UserGetResponse,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def get_user(
    request: Request,
    user_id: UUID,
    user_service: UserService = Depends(),
):
    user = await user_service.get_user(user_id)

    return UserGetResponse.model_validate(user)


@router.patch(
    "/me",
    response_model=UserUpdateResponse,
    dependencies=[Depends(RoleBasedLimiter)],
)
async def patch_user(
    request: Request,
    user_data: UserPatchRequest,
    user_id: UUID = Depends(get_user_id_from_token),
    user_service: UserService = Depends(),
):
    await user_service.update_user(user_id, user_data)

    return UserUpdateResponse()


@router.delete(
    "/me",
    response_model=UserDeleteResponse,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def delete_user(
    request: Request,
    user_id: UUID = Depends(get_user_id_from_token),
    user_service: UserService = Depends(),
) -> UserDeleteResponse:
    await user_service.remove_user(user_id)

    return UserDeleteResponse()
