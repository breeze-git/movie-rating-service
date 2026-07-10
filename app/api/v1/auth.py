from secrets import compare_digest

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_tokens_pair
from app.database.storage import REFRESH_TOKENS
from app.schemas.auth import (
    Token,
    TokensResponse,
    UserRegisterRequest,
    UserRegisterResponse,
)
from app.services.users import UserService

from .dependencies import IPBasedLimiter, decode_token_safely, verify_claims

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def register_user(
    request: Request,
    user_data: UserRegisterRequest,
    user_service: UserService = Depends(),
) -> UserRegisterResponse:
    await user_service.register_user(user_data)

    return UserRegisterResponse()


@router.post(
    "/login",
    response_model=TokensResponse,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(),
) -> TokensResponse:
    user = await user_service.authenticate_user(email=form_data.username, password=form_data.password)

    tokens_data = create_tokens_pair(user.id)

    return TokensResponse(**tokens_data)


@router.post(
    "/refresh",
    response_model=TokensResponse,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def refresh_token(request: Request, token: Token) -> TokensResponse:
    payload = decode_token_safely(token.refresh_token)

    verify_claims(payload, req_token_type="refresh")

    user_id = payload["sub"]

    user_token = REFRESH_TOKENS.get(user_id)

    if user_token is None or not compare_digest(user_token, token.refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from None

    response_data = create_tokens_pair(user_id)

    return TokensResponse(**response_data)
