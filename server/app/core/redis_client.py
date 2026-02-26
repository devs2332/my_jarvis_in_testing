"""
Redis client for rate limiting, caching, and job queues.
"""

import json
import logging
from typing import Optional, Any

import redis.asyncio as aioredis

from server.app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_redis_pool: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get or create the Redis connection pool."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )
    return _redis_pool


async def close_redis():
    """Close the Redis connection pool."""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None


# ── Rate Limiting ────────────────────────────────────────

async def check_rate_limit(
    user_id: str, limit: int, window_seconds: int = 60
) -> tuple[bool, int]:
    """
    Sliding window rate limiter.
    Returns (allowed: bool, remaining: int).
    """
    r = await get_redis()
    key = f"rate_limit:{user_id}"

    import time
    now = time.time()
    window_start = now - window_seconds

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window_seconds)
    results = await pipe.execute()

    current_count = results[2]
    allowed = current_count <= limit
    remaining = max(0, limit - current_count)

    if not allowed:
        # Remove the request we just added since it's denied
        await r.zrem(key, str(now))

    return allowed, remaining


# ── Caching ──────────────────────────────────────────────

async def cache_set(key: str, value: Any, ttl: int = None) -> None:
    """Set a value in the cache."""
    r = await get_redis()
    ttl = ttl or settings.REDIS_CACHE_TTL
    serialized = json.dumps(value) if not isinstance(value, str) else value
    await r.set(f"cache:{key}", serialized, ex=ttl)


async def cache_get(key: str) -> Optional[Any]:
    """Get a value from the cache."""
    r = await get_redis()
    value = await r.get(f"cache:{key}")
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


async def cache_delete(key: str) -> None:
    """Delete a cache key."""
    r = await get_redis()
    await r.delete(f"cache:{key}")


# ── Job Queue ────────────────────────────────────────────

async def enqueue_job(queue_name: str, job_data: dict) -> None:
    """Push a job onto a Redis list queue."""
    r = await get_redis()
    await r.rpush(f"queue:{queue_name}", json.dumps(job_data))


async def dequeue_job(queue_name: str, timeout: int = 0) -> Optional[dict]:
    """
    Pop a job from the queue (blocking if timeout > 0).
    Returns None if no job available within timeout.
    """
    r = await get_redis()
    result = await r.blpop(f"queue:{queue_name}", timeout=timeout)
    if result:
        _, data = result
        return json.loads(data)
    return None
