import inspect
import logging
from collections.abc import Callable
from datetime import timedelta
from functools import wraps
from typing import Any

from pydantic import BaseModel, TypeAdapter
from redis import RedisError

from app.redis import get_redis

logger = logging.getLogger(__name__)


def build_cache_key(func: Callable, template: str, *args, **kwargs):
    signature = inspect.signature(func)
    bound = signature.bind(None, *args, **kwargs)

    cache_key = template.format(**bound.arguments)

    return cache_key


def cached(*, key: str, schema: Any, ttl: int | timedelta | None = None) -> Callable:
    def decorator(func) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> BaseModel:
            cache_key = build_cache_key(func, key, *args, **kwargs)

            adapter = TypeAdapter(schema)

            redis_client = get_redis()

            try:
                cached = await redis_client.get(cache_key)
            except RedisError:
                logger.warning(
                    "Redis cache is unavailable. Falling back to database.",
                    exc_info=True,
                )
                cached = None

            if cached is not None:
                return adapter.validate_json(cached)

            result = await func(self, *args, **kwargs)
            try:
                await redis_client.set(cache_key, adapter.dump_json(result), ttl)
            except RedisError:
                logger.warning(
                    "Failed to write cache entry.",
                    exc_info=True,
                )

            return result

        return wrapper

    return decorator


def invalidate_cache(*, key: str) -> Callable:
    def decorator(func) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> BaseModel:
            result = await func(self, *args, **kwargs)

            cache_key = build_cache_key(func, key, *args, **kwargs)

            redis_client = get_redis()

            try:
                await redis_client.delete(cache_key)
            except RedisError:
                logger.warning(
                    "Failed to delete cache entry.",
                    exc_info=True,
                )

            return result

        return wrapper

    return decorator
