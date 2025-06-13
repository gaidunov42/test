import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from jose import JWTError, jwt
from fastapi import HTTPException

from app.jwt_config import settings_jwt
from app.services.refresh_store import RedisRefreshTokenStore


class JWTService:
    def __init__(self):
        self.secret_key = settings_jwt.JWT_SECRET
        self.algorithm = settings_jwt.JWT_ALGORITHM
        self.access_token_ttl = timedelta(
            minutes=settings_jwt.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        self.refresh_token_ttl = timedelta(days=settings_jwt.REFRESH_TOKEN_EXPIRE_DAYS)
        self.redis_store = RedisRefreshTokenStore()

    def _create_payload(
        self,
        user_id: str,
        permissions: list,
        token_type: str,
        ttl: timedelta,
        jti: Optional[str] = None,
    ) -> dict:
        now = datetime.now(timezone.utc)
        return {
            "user_id": user_id,
            "permissions": permissions,
            "jti": jti or str(uuid.uuid4()),
            "type": token_type,
            "iat": now,
            "exp": now + ttl,
        }

    def _encode(self, payload: dict) -> str:
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Недействительный токен")

    def create_access_token(self, user_id: str, permissions: list) -> str:
        payload = self._create_payload(
            user_id, permissions, "access", self.access_token_ttl
        )
        return self._encode(payload)

    async def create_refresh_token(
        self, user_id: str, permissions: list, metadata: dict
    ) -> str:
        payload = self._create_payload(
            user_id, permissions, "refresh", self.refresh_token_ttl
        )
        token = self._encode(payload)

        await self.redis_store.save_token(
            user_id=user_id,
            token_id=payload["jti"],
            payload=metadata,
            ttl=int(self.refresh_token_ttl.total_seconds()),
        )
        return token

    async def verify_refresh_token(self, token: str) -> dict:
        payload = self.decode_token(token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Недопустимый тип токена")

        user_id = payload["user_id"]
        token_id = payload["jti"]

        exists = await self.redis_store.get_token(user_id, token_id)
        if not exists:
            raise HTTPException(
                status_code=401, detail="Refresh токен отозван или истёк"
            )

        return payload

    async def rotate_tokens(
        self, refresh_token: str, metadata: dict
    ) -> Tuple[str, str]:
        old_payload = await self.verify_refresh_token(refresh_token)
        await self.redis_store.delete_token(old_payload["user_id"], old_payload["jti"])
        access = self.create_access_token(
            old_payload["user_id"], old_payload["permissions"]
        )
        refresh = await self.create_refresh_token(
            old_payload["user_id"], old_payload["permissions"], metadata
        )

        return access, refresh

    def verify_access_token(self, token: str) -> dict:
        """
        Проверяет access_token:
        - валидна ли подпись
        - не истёк ли срок
        - является ли токеном типа 'access'
        Возвращает payload.
        """
        payload = self.decode_token(token)

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Недопустимый тип токена")

        return payload

    def get_user_id_from_token(self, token: str) -> str:
        """
        Декодирует access_token и возвращает user_id.
        """
        payload = self.verify_access_token(token)
        return payload["user_id"]


jwt_service = JWTService()
