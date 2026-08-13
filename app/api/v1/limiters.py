from fastapi import Depends, Request
from limits import parse
from limits.aio import strategies
from limits.aio.storage import RedisStorage
from redis.asyncio import Redis

from app.core.exceptions.http import RateLimitExceededError
from app.core.settings import settings
from app.services.users.service import UserService

from .dependencies import get_current_user_claims


class RateLimiter:
    def init_storage(self, redis_client: Redis, redis_url: str) -> None:
        storage = RedisStorage(
            redis_url,
            implementation="redispy",
            connection_pool=redis_client.connection_pool,  # type: ignore[arg-type]  # limits 5.8.0 supports ConnectionPool at runtime
        )

        self.moving_window = strategies.MovingWindowRateLimiter(storage)

    async def check_limit(self, user_identifier: str, endpoint_name: str, limit: str) -> None:
        limit_item = parse(limit)

        if not await self.moving_window.hit(limit_item, user_identifier, endpoint_name):
            raise RateLimitExceededError(
                limit=limit,
                user_identifier=user_identifier,
                retry_after=limit_item.get_expiry(),
            ) from None

    def is_test_mode(self) -> bool:
        return settings.mode == "TEST"


limiter = RateLimiter()


class RoleBasedLimiter:
    async def __call__(
        self,
        request: Request,
        payload: dict = Depends(get_current_user_claims),
        user_service: UserService = Depends(),
    ) -> None:
        if limiter.is_test_mode():
            return

        user_id = payload["sub"]
        user_roles = await user_service.get_user_roles(user_id)

        user_identifier = f"user:{user_id}"
        limit = "20/minute"

        if "admin" in user_roles:
            limit = "1000/minute"

        endpoint_name = request.url.path

        await limiter.check_limit(user_identifier, endpoint_name, limit)


class IPBasedLimiter:
    def __init__(self, limit: str):
        self.limit: str = limit

    async def __call__(self, request: Request):
        if limiter.is_test_mode():
            return

        client = request.client

        if client is None:
            raise RuntimeError("Client information is unavailable.")

        user_identifier = client.host
        endpoint_name = request.url.path

        await limiter.check_limit(user_identifier, endpoint_name, self.limit)
