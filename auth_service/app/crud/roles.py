from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import async_session_maker
from app.models.db import Role, Permission

from typing import List


class RolesCrud:
    model = Role

    @classmethod
    async def roles_with_permissions(
        cls,
    ):
        async with async_session_maker() as session:
            result = await session.execute(
                select(Role).options(selectinload(Role.permissions))
            )
            roles = result.scalars().all()
        return roles

    @staticmethod
    async def get_role_by_name(name: str) -> Role:
        async with async_session_maker() as session:
            result = await session.execute(select(Role).where(Role.name == name))
            return result.scalar_one_or_none()

    @staticmethod
    async def create_role(
        name: str, description: str, permission_codes: List[str]
    ) -> Role:
        async with async_session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(Permission).where(Permission.code.in_(permission_codes))
                )
                permissions = result.scalars().all()

                new_role = Role(
                    name=name, description=description, permissions=permissions
                )
                session.add(new_role)
            await session.refresh(new_role)
            await session.execute(
                select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.id == new_role.id)
            )

            return new_role

    @staticmethod
    async def get_by_code(code: str) -> Permission | None:
        async with async_session_maker() as session:
            result = await session.execute(
                select(Permission).where(Permission.code == code)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def create(code: str, description: str) -> Permission:
        async with async_session_maker() as session:
            async with session.begin():
                permission = Permission(code=code, description=description)
                session.add(permission)
                await session.flush()
                await session.refresh(permission)
                return permission
