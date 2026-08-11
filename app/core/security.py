import json
from datetime import UTC, datetime, timedelta
from uuid import UUID

import bcrypt
import jwt

from app.redis import get_redis

from .settings import settings


def get_hash(password: str) -> bytes:
    bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)

    return hash


def verify_password(password: str, hashed_password: str):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


async def get_user_data_by_token(token: str) -> dict | None:
    redis_client = get_redis()

    raw_json = await redis_client.get(token)

    if raw_json is None:
        return

    return json.loads(raw_json)


def set_access_token(data: dict) -> str:
    to_encode = data.copy()

    utc_now = datetime.now(UTC)
    expire_at = utc_now + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire_at, "type": "access"})

    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return token


async def set_refresh_token(data: dict) -> str:
    to_encode = data.copy()

    utc_now = datetime.now(UTC)
    expire_after = timedelta(days=settings.refresh_token_expire_days)

    expire_at = utc_now + expire_after
    to_encode.update({"exp": expire_at, "type": "refresh"})

    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    redis_client = get_redis()

    await redis_client.set(token, json.dumps(data), timedelta(seconds=10))

    return token


async def create_tokens_pair(user_id: UUID) -> dict:
    user_id_str = str(user_id)

    data = {"sub": user_id_str}

    access_token = set_access_token(data)
    refresh_token = await set_refresh_token(data)

    response_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

    return response_data
