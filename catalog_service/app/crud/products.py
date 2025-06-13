from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete

from app.db import async_session_maker
from app.crud.base import BaseCrud
from app.models.db import Products


class Product(BaseCrud):
    model = Products

    @classmethod
    async def find_product_all(cls):
        async with async_session_maker() as session:
            query = select(cls.model).options(selectinload(cls.model.category))
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_product_one_or_none_by_id(cls, id_product: int):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.id == id_product)
                .options(selectinload(cls.model.category))
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def update_product(cls, product_id: int, **values) -> int:
        async with async_session_maker() as session:
            async with session.begin():

                query = (
                    sqlalchemy_update(cls.model)
                    .where(cls.model.id == product_id)
                    .values(**values)
                    .execution_options(synchronize_session="fetch")
                )
                result = await session.execute(query)
                return result.rowcount
