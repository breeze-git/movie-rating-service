from datetime import UTC, datetime, timedelta
from secrets import compare_digest
from uuid import UUID

import asyncpg
import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from limits import strategies
from limits.storage import MemoryStorage

from app.database.database import get_session
from app.database.repositories import get_review_owner, get_user_permissions
from app.database.storage import REFRESH_TOKENS, config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_MINUTES = 3

storage = MemoryStorage()
moving_window = strategies.MovingWindowRateLimiter(storage)


def get_token_payload(token: str) -> dict:
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=config.algorithm)

        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired"
        ) from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from None


def get_current_user_claims(token: str = Depends(oauth2_scheme)) -> dict:
    payload = get_token_payload(token)

    return payload


def get_hash(password: str) -> bytes:
    bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)

    return hash


def set_access_token(data: dict) -> str:
    to_encode = data.copy()

    utc_now = datetime.now(UTC)
    expire_at = utc_now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire_at, "type": "access"})

    token = jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)

    return token


def set_refresh_token(data: dict) -> str:
    to_encode = data.copy()

    utc_now = datetime.now(UTC)
    expire_at = utc_now + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire_at, "type": "refresh"})

    token = jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)

    return token


def create_tokens_pair(user_id: UUID) -> dict:
    user_id_str = str(user_id)

    data = {"sub": user_id_str}

    access_token = set_access_token(data)
    refresh_token = set_refresh_token(data)

    REFRESH_TOKENS[user_id_str] = refresh_token

    response_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

    return response_data


async def verify_permissions(
    request: Request,
    security_scopes: SecurityScopes,
    payload: dict = Depends(get_current_user_claims),
    session: asyncpg.Connection = Depends(get_session),
    review_id: str | None = None,
) -> str:
    user_id = payload.get("sub")
    token_type = payload.get("type")

    if user_id is None or token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from None

    if review_id is not None:
        owner_id = await get_review_owner(review_id, session)

        if owner_id is not None and compare_digest(str(owner_id), user_id):
            return user_id

    required_scopes = security_scopes.scopes
    user_permissions = await get_user_permissions(user_id, session)

    if not user_permissions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from None

    for scope in required_scopes:
        if scope not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough rights",
            ) from None

    return user_id
