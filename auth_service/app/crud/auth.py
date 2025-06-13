from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.db import async_session_maker
from app.models.db import User, Role
from app.services.work_with_pass import hash_password, verify_password

import uuid


class UserCrud:
    model = User

    @classmethod
    async def create(cls, email: str, full_name: str, password: str):
        async with async_session_maker() as session:
            try:
                user_exists = await session.execute(
                    select(User).where(User.email == email)
                )
                if user_exists.scalar_one_or_none():
                    raise ValueError("Пользователь с таким email уже существует")
                result = await session.execute(select(Role).where(Role.name == "user"))
                user_role = result.scalar_one_or_none()
                if not user_role:
                    raise ValueError("Роль 'user' не найдена")
                new_user = User(
                    id=uuid.uuid4(),
                    email=email,
                    name=full_name,
                    password_hash=hash_password(password),
                    role_id=user_role.id,
                )
                session.add(new_user)
                await session.commit()
                return new_user
            except SQLAlchemyError as e:
                await session.rollback()
                raise RuntimeError(f"Ошибка при создании пользователя: {e}")

    @classmethod
    async def authenticate(cls, email: str, password: str) -> User:
        """
        Проверяет email и пароль. Возвращает пользователя с подгруженными permissions.
        """
        async with async_session_maker() as session:
            result = await session.execute(
                select(User)
                .options(selectinload(User.role).selectinload(Role.permissions))
                .where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if not user or not verify_password(password, user.password_hash):
                raise ValueError("Неверный email или пароль")

            return user

    @classmethod
    async def get_by_id(cls, user_id: str) -> User:
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).options(selectinload(User.role)).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
