from secrets import compare_digest
from typing import Annotated

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Request, status
from starlette.status import HTTP_409_CONFLICT

from app.core.exceptions import UsernameAlredyExistsError
from app.core.limiters import IPBasedLimiter
from app.core.security import create_tokens_pair, get_token_payload
from app.database.database import get_session
from app.database.repositories import get_user_from_db_by_email
from app.database.storage import REFRESH_TOKENS
from app.schemas.auth import CreateUser, CreateUserResp, TokensResp, UserInDB, UserToken
from app.services.auth import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=CreateUserResp,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def register_user(
    request: Request,
    user: CreateUser,
    session: asyncpg.Connection = Depends(get_session),
) -> CreateUserResp:
    alredy_exists = await get_user_from_db_by_email(user.email, session)

    if alredy_exists is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists") from None

    try:
        await create_user(user, session)
    except UsernameAlredyExistsError:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="User with this username already exists",
        ) from None

    return CreateUserResp()


@router.post(
    "/login",
    response_model=TokensResp,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def login_user(request: Request, user: Annotated[UserInDB | None, Depends(authenticate_user)]) -> TokensResp:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed") from None

    response_data = create_tokens_pair(user.id)

    return TokensResp(**response_data)


@router.post(
    "/refresh",
    response_model=TokensResp,
    dependencies=[Depends(IPBasedLimiter("5/minute"))],
)
async def refresh_token(request: Request, token: UserToken) -> TokensResp:
    payload = get_token_payload(token.refresh_token)

    user_id = payload.get("sub")
    token_type = payload.get("type")

    if user_id is not None and token_type == "refresh":
        user_token = REFRESH_TOKENS.get(user_id)
        print(REFRESH_TOKENS)

        if user_token is not None and compare_digest(user_token, token.refresh_token):
            response_data = create_tokens_pair(user_id)

            return TokensResp(**response_data)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from None
