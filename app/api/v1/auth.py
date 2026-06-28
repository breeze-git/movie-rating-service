from secrets import compare_digest

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.security import create_tokens_pair
from app.database.storage import REFRESH_TOKENS
from app.schemas.auth import (
    Token,
    TokensResponse,
    UserCreateRequest,
    UserCreateResponse,
    UserDeleteResponse,
    UserLoginRequest,
)
from app.services.auth import UserService

from .dependencies import IPBasedLimiter, decode_token_safely, get_current_user_claims

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def register_user(
    request: Request,
    user_data: UserCreateRequest,
    user_service: UserService = Depends(),
) -> UserCreateResponse:

    await user_service.create_new_user(user_data)

    return UserCreateResponse()


@router.post(
    "/login",
    response_model=TokensResponse,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def login_user(
    request: Request,
    user_data: UserLoginRequest,
    user_service: UserService = Depends(),
) -> TokensResponse:

    user = await user_service.authenticate_user(user_data)

    response_data = create_tokens_pair(user.id)

    return TokensResponse(**response_data)


@router.post(
    "/refresh",
    response_model=TokensResponse,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def refresh_token(request: Request, token: Token) -> TokensResponse:
    payload = decode_token_safely(token.refresh_token)

    user_id = payload.get("sub")
    token_type = payload.get("type")

    if user_id is not None and token_type == "refresh":
        user_token = REFRESH_TOKENS.get(user_id)

        if user_token is not None and compare_digest(user_token, token.refresh_token):
            response_data = create_tokens_pair(user_id)

            return TokensResponse(**response_data)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
    ) from None


@router.delete(
    "/delete",
    response_model=UserDeleteResponse,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def delete_user(
    request: Request,
    payload: dict = Depends(get_current_user_claims),
    user_service: UserService = Depends(),
) -> UserDeleteResponse:
    user_id = payload.get("sub")
    token_type = payload.get("type")

    if user_id is None or token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from None

    await user_service.remove_user(user_id)

    return UserDeleteResponse()
