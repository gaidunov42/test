from app.redis.redis_client import get_redis
from typing import Any, Optional
import json

from app.crud.categories import Category
from app.crud.products import Product


class RedisCache:
    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl  # TTL в секундах (по умолчанию 1 час)

    async def set_value(self, key: str, data: Category | Product):
        """
        Добавить значение в кэш или обновить его.
        Значение сериализуется в JSON.
        """
        categories_data = [cat.to_dict() for cat in data]
        redis = await get_redis()
        value_str = json.dumps(categories_data)
        await redis.set(key, value_str, ex=self.default_ttl)

    async def get_value(self, key: str) -> Optional[Any]:
        """
        Получить значение из кэша.
        Если ключа нет — вернёт None.
        """
        redis = await get_redis()
        value = await redis.get(key)
        if value is not None:
            return json.loads(value)
        return None

    async def delete_value(self, key: str):
        """
        Удалить значение из кэша по ключу.
        """
        redis = await get_redis()
        await redis.delete(key)


cash = RedisCache()
