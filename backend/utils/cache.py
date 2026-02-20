"""
Redis caching utilities with decorator support
"""

import hashlib
import json
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar, cast

import redis.asyncio as redis

from config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)

T = TypeVar("T")


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()


def cache(expire: int = 300, prefix: str = "api"):
    """
    Cache decorator for expensive operations
    Args:
        expire: TTL in seconds (default 5 min)
        prefix: Cache key prefix
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            key = f"{prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            cached = await redis_client.get(key)
            if isinstance(cached, str) and cached:
                return cast(T, json.loads(cached))
            result = await func(*args, **kwargs)
            await redis_client.setex(key, expire, json.dumps(result))
            return result

        return wrapper

    return decorator


async def invalidate_cache(pattern: str):
    """Invalidate cache keys matching pattern"""
    async for key in redis_client.scan_iter(match=pattern):
        await redis_client.delete(key)
