from redis.asyncio import Redis


class RedisHelper:
    def __init__(self) -> None:
        self.client: Redis | None = None

    async def init(self, url: str) -> None:
        self.client = Redis.from_url(url, decode_responses=True)

    async def close(self) -> None:
        if self.client:
            await self.client.aclose()

    def get_client(self) -> Redis:
        if self.client is None:
            raise RuntimeError("Redis client is not initialized! Ensure init() was called in lifespan.")
        return self.client


redis_helper = RedisHelper()


def get_redis() -> Redis:
    return redis_helper.get_client()
