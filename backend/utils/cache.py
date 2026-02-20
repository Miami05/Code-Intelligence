"""
Redis caching utilities with decorator support.
Works with both sync (def) and async (async def) FastAPI endpoints.
"""

import asyncio
import functools
import hashlib
import json
from typing import Any, Callable, Optional, cast

import redis as redis_lib
from redis import Redis

from config import settings

redis_client: Optional[redis_lib.Redis] = None
REDIS_AVAILABLE = False

try:
    redis_client = redis_lib.from_url(settings.redis_url, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception:
    print("⚠️  Redis not available — caching disabled")
    redis_client = None
    REDIS_AVAILABLE = False


def _make_key(prefix: str, func_name: str, args, kwargs) -> str:
    """Generate a stable cache key from function name + arguments."""
    raw = f"{args}{sorted(kwargs.items())}"
    hashed = hashlib.md5(raw.encode()).hexdigest()
    return f"{prefix}:{func_name}:{hashed}"


def _serialize(value: Any) -> str:
    return json.dumps(value, default=str)


def _deserialize(value: str) -> Any:
    return json.loads(value)


def cache(expire: int = 300, prefix: str = "api"):
    """
    Cache decorator for FastAPI endpoints.
    Supports both sync `def` and async `async def` route handlers.

    Args:
        expire: TTL in seconds (default: 300 = 5 minutes)
        prefix: Redis key prefix for grouping (e.g. 'call_graph', 'search')
    """

    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not REDIS_AVAILABLE or redis_client is None:
                    return await func(*args, **kwargs)
                key = _make_key(prefix, func.__name__, args, kwargs)
                cached = await asyncio.to_thread(redis_client.get, key)
                if isinstance(cached, str):
                    return _deserialize(cached)
                result = await func(*args, **kwargs)
                try:
                    await asyncio.to_thread(
                        redis_client.setex, key, expire, _serialize(result)
                    )
                except Exception as e:
                    print(f"⚠️  Cache write failed: {e}")
                return result

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not REDIS_AVAILABLE or redis_client is None:
                    return func(*args, **kwargs)
                key = _make_key(prefix, func.__name__, args, kwargs)
                cached = redis_client.get(key)
                if isinstance(cached, str):
                    return _deserialize(cached)
                result = func(*args, **kwargs)
                try:
                    redis_client.setex(key, expire, _serialize(result))
                except Exception as e:
                    print(f"⚠️ Cache write failed: {e}")
                return result

            return sync_wrapper

    return decorator


def invalidate_cache(pattern: str):
    """Invalidate all cache keys matching a pattern (e.g. 'call_graph:*')"""
    if not REDIS_AVAILABLE or redis_client is None:
        return
    try:
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)
    except Exception as e:
        print(f"⚠️  Cache invalidation failed: {e}")
