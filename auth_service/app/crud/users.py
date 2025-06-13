from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.db import User
from app.db import async_session_maker
from app.schemas.schemas import UserUpdateRequest


class UserCrud:

    @staticmethod
    async def update_user(data: UserUpdateRequest) -> User:
        async with async_session_maker() as session:
            async with session.begin():
                result = await session.execute(select(User).where(User.id == data.id))
                user = result.scalar_one_or_none()
                if not user:
                    raise ValueError("Пользователь не найден")
                if data.email is not None:
                    user.email = data.email
                if data.name is not None:
                    user.name = data.name
                if data.role_id is not None:
                    user.role_id = data.role_id
            result = await session.execute(
                select(User).options(selectinload(User.role)).where(User.id == data.id)
            )
            return result.scalar_one()
