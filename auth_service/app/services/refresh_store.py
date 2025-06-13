from app.redis.redis_client import get_redis
from typing import Optional
import json


class RedisRefreshTokenStore:
    def __init__(
        self,
    ):
        self.default_ttl: int = 7 * 24 * 3600

    async def save_token(
        self, user_id: str, token_id: str, payload: dict, ttl: Optional[int] = None
    ):
        """
        Сохраняет refresh token в Redis.
        Ключ: refresh:{user_id}:{token_id}
        Значение: JSON с полезными данными (user_agent, ip и т.д.)
        """
        redis = await get_redis()
        key = f"refresh:{user_id}:{token_id}"
        value = json.dumps(payload)
        await redis.set(key, value, ex=ttl or self.default_ttl)

    async def get_token(self, user_id: str, token_id: str) -> Optional[dict]:
        """
        Получает refresh token по ключу.
        Если не найден — возвращает None.
        """
        redis = await get_redis()
        key = f"refresh:{user_id}:{token_id}"
        value = await redis.get(key)
        if value is not None:
            return json.loads(value)
        return None

    async def delete_token(self, user_id: str, token_id: str):
        """
        Удаляет refresh token по ключу (например, при logout).
        """
        redis = await get_redis()
        key = f"refresh:{user_id}:{token_id}"
        await redis.delete(key)

    async def delete_all_tokens_for_user(self, user_id: str):
        """
        Удаляет все refresh токены пользователя (logout со всех устройств).
        """
        redis = await get_redis()
        pattern = f"refresh:{user_id}:*"
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)
