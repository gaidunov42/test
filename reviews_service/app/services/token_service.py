import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from jose import JWTError, jwt
from fastapi import HTTPException

from app.jwt_config import settings_jwt


class JWTService:
    def __init__(self):
        self.secret_key = settings_jwt.JWT_SECRET
        self.algorithm = settings_jwt.JWT_ALGORITHM

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Недействительный токен")

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
