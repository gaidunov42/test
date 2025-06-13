from typing import Optional

import redis
from redis import Redis
from loguru import logger

from app.redis.redis_config import get_redis_url

redis_client: Optional[Redis] = None


def reconnect_redis():
    global redis_client
    if redis_client:
        try:
            redis_client.close()
        except Exception as e:
            logger.error(f"Error while closing Redis: {e}")
    redis_client = redis.Redis.from_url(get_redis_url(), decode_responses=True)
    logger.info("Redis reconnected.")


def get_redis() -> Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis.from_url(get_redis_url(), decode_responses=True)

    try:
        redis_client.ping()
    except Exception:
        reconnect_redis()

    return redis_client
