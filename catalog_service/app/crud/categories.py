from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete

from app.db import async_session_maker
from app.crud.base import BaseCrud
from app.models.db import Categories


class Category(BaseCrud):
    model = Categories

    @classmethod
    async def update_category(cls, category_id: int, **values):
        async with async_session_maker() as session:
            async with session.begin():
                query = (
                    sqlalchemy_update(cls.model)
                    .where(cls.model.id == category_id)
                    .values(**values)
                    .execution_options(synchronize_session="fetch")
                )
                result = await session.execute(query)
                return result

    @classmethod
    async def delete_category(cls, category_id: int):
        async with async_session_maker() as session:
            async with session.begin():
                query = sqlalchemy_delete(cls.model).filter_by(id=category_id)
                result = await session.execute(query)
                return result
