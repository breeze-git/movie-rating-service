from secrets import compare_digest

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import REFRESH_TOKENS, create_tokens_pair
from app.schemas.auth import RefreshToken, Tokens, UserRegister
from app.schemas.common import ResponseEnvelope
from app.schemas.users import UserBrief
from app.services.users.service import UserService

from .dependencies import IPBasedLimiter, decode_token_safely, verify_claims
from .openapi import errors_model

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    name="register_user",
    response_model=ResponseEnvelope[UserBrief],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 409, 422, 429),
)
async def register_user(
    request: Request,
    payload: UserRegister,
    service: UserService = Depends(),
) -> ResponseEnvelope:
    user = await service.register_user(payload)

    return ResponseEnvelope(data=user)


@router.post(
    "/login",
    name="login_user",
    response_model=ResponseEnvelope[Tokens],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 401, 422, 429),
)
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(),
) -> ResponseEnvelope:
    user_id = await service.authenticate_user(email=form_data.username, password=form_data.password)

    tokens_data = create_tokens_pair(user_id)

    return ResponseEnvelope(data=tokens_data)


@router.post(
    "/refresh",
    name="refresh_token",
    response_model=ResponseEnvelope[Tokens],
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
    responses=errors_model(400, 401, 422, 429),
)
async def refresh_token(request: Request, token: RefreshToken) -> ResponseEnvelope:
    payload = decode_token_safely(token.refresh_token)

    verify_claims(payload, req_token_type="refresh")

    user_id = payload["sub"]

    user_token = REFRESH_TOKENS.get(user_id)

    if user_token is None or not compare_digest(user_token, token.refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from None

    tokens_data = create_tokens_pair(user_id)

    return ResponseEnvelope(data=tokens_data)
