import asyncpg
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from limits import parse, strategies
from limits.storage import MemoryStorage

from app.core.config import load_config
from app.core.security import get_current_user_claims
from app.database.database import get_session
from app.database.repositories import get_user_roles

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

config = load_config()


REFRESH_TOKENS = {}

ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_MINUTES = 3

storage = MemoryStorage()
moving_window = strategies.MovingWindowRateLimiter(storage)


class RoleBasedLimiter:
    async def __call__(
        self,
        request: Request,
        payload: dict = Depends(get_current_user_claims),
        session: asyncpg.Connection = Depends(get_session),
    ) -> None:
        user_id = payload.get("sub")
        user_roles = await get_user_roles(user_id, session)

        if not user_roles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user_identifier = f"user:{user_id}"
        limit = "20/minute"

        if "admin" in user_roles:
            limit = "1000/minute"

        endpoint_name = request.url.path

        check_limit(user_identifier, endpoint_name, limit)


class IPBasedLimiter:

    def __init__(self, limit: str):
        self.limit: str = limit

    def __call__(self, request: Request):
        user_identifier = request.client.host  # type: ignore
        endpoint_name = request.url.path

        check_limit(user_identifier, endpoint_name, self.limit)


def check_limit(user_identifier: str, endpoint_name: str, limit: str) -> None:
    limit_item = parse(limit)

    if not moving_window.hit(limit_item, user_identifier, endpoint_name):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {limit}",
        ) from None
