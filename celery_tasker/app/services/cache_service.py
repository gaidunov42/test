from app.redis.redis_client import get_redis
from typing import Any, Optional
import json


class RedisCache:
    def __init__(self, default_ttl: int = 60):
        self.default_ttl = default_ttl

    def set_value(self, key: str, data):
        """
        Добавить значение в кэш или обновить его.
        Значение сериализуется в JSON.
        """
        redis = get_redis()
        redis.set(key, data, ex=self.default_ttl)

    def get_value(self, key: str) -> Optional[Any]:
        """
        Получить значение из кэша.
        Если ключа нет — вернёт None.
        """
        redis = get_redis()
        value = redis.get(key)
        if value is not None:
            return value
        return None


cash = RedisCache()
