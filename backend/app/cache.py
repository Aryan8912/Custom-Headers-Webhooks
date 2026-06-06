import json
import redis.asyncio as aioredis
from typing import Optional, Any
from app.config import get_settings

settings = get_settings()

# ── Redis client (single instance) ────────────────────
redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Return the shared Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def close_redis():
    """Close Redis connection on app shutdown."""
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None


# ── Helpers ────────────────────────────────────────────
async def cache_get(key: str) -> Optional[Any]:
    """Get a JSON value from Redis. Returns None if missing."""
    r = await get_redis()
    value = await r.get(key)
    if value is None:
        return None
    return json.loads(value)


async def cache_set(key: str, value: Any, ttl: int = 300):
    """Store a JSON value in Redis with TTL (default 5 min)."""
    r = await get_redis()
    await r.setex(key, ttl, json.dumps(value))


async def cache_delete(key: str):
    """Delete a key from Redis."""
    r = await get_redis()
    await r.delete(key)


async def cache_exists(key: str) -> bool:
    """Check if a key exists in Redis."""
    r = await get_redis()
    return await r.exists(key) == 1