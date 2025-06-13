from typing import Optional
import asyncio

import aioredis
from aioredis import Redis
from loguru import logger

from app.redis.redis_config import get_redis_url

redis: Optional[Redis] = None
lock = asyncio.Lock()


async def reconnect_redis():
    global redis
    if redis:
        try:
            await redis.close()
        except Exception as e:
            logger.info(f"Error while closing Redis: {e}")

    redis = aioredis.from_url(get_redis_url(), decode_responses=True)
    logger.info("Redis reconnected.")


async def get_redis() -> Redis:
    global redis
    async with lock:
        if redis is None:
            redis = aioredis.from_url(get_redis_url(), decode_responses=True)
        try:
            await redis.ping()
        except Exception as e:
            await reconnect_redis()

    return redis
