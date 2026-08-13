from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.exceptions.http import SessionExpiredError
from app.core.security import (
    create_tokens_pair,
    delete_refresh_token,
    get_user_data_by_token,
)
from app.schemas.auth import RefreshToken, Tokens, UserRegister
from app.schemas.common import ResponseEnvelope
from app.schemas.users import UserDetail
from app.services.users.service import UserService

from .dependencies import decode_token_safely, verify_claims
from .limiters import IPBasedLimiter
from .openapi import errors_model

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    name="register_user",
    summary="Register a new user",
    response_model=ResponseEnvelope[UserDetail],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 409, 422, 429),
)
async def register_user(
    payload: UserRegister,
    service: UserService = Depends(),
) -> ResponseEnvelope:
    user = await service.register_user(payload)

    return ResponseEnvelope(data=user)


@router.post(
    "/login",
    name="login_user",
    summary="Authenticate user",
    response_model=ResponseEnvelope[Tokens],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 401, 422, 429),
)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(),
) -> ResponseEnvelope:
    user_id = await service.authenticate_user(email=form_data.username, password=form_data.password)

    tokens_data = await create_tokens_pair(user_id)

    return ResponseEnvelope(data=tokens_data)


@router.post(
    "/refresh",
    name="refresh_token",
    summary="Refresh access token",
    description="""Creates a new access token using a valid refresh token.

Requires a refresh token in the request body.""",
    response_model=ResponseEnvelope[Tokens],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 401, 422, 429),
)
async def refresh_token(token: RefreshToken) -> ResponseEnvelope:
    payload = decode_token_safely(token.refresh_token)

    verify_claims(payload, req_token_type="refresh")

    user_id = payload["sub"]

    data = await get_user_data_by_token(token.refresh_token)

    if data is None or data.get("sub") != user_id:
        raise SessionExpiredError()

    tokens_data = await create_tokens_pair(user_id)

    await delete_refresh_token(token.refresh_token)

    return ResponseEnvelope(data=tokens_data)


@router.post(
    "/logout",
    name="logout_user",
    summary="Logout current user",
    description="""Invalidates the current refresh token.

    Requires a refresh token in the request body.""",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 401, 422, 429),
)
async def logout_user(token: RefreshToken) -> None:
    decode_token_safely(token.refresh_token)

    data = await get_user_data_by_token(token.refresh_token)

    if data is None:
        raise SessionExpiredError()

    await delete_refresh_token(token.refresh_token)
