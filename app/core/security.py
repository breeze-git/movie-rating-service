from datetime import UTC, datetime, timedelta
from uuid import UUID

import bcrypt
import jwt

from .settings import settings

REFRESH_TOKENS = {}


def get_hash(password: str) -> bytes:
    bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)

    return hash


def verify_password(password: str, hashed_password: str):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def set_access_token(data: dict) -> str:
    to_encode = data.copy()

    utc_now = datetime.now(UTC)
    expire_at = utc_now + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire_at, "type": "access"})

    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return token


def set_refresh_token(data: dict) -> str:
    to_encode = data.copy()

    utc_now = datetime.now(UTC)
    expire_at = utc_now + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({"exp": expire_at, "type": "refresh"})

    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

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
