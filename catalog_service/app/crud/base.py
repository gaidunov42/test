from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete

from app.db import async_session_maker


class BaseCrud:
    model = None

    @classmethod
    async def find_all(cls):
        async with async_session_maker() as session:
            query = select(cls.model)
            students = await session.execute(query)
            return students.scalars().all()

    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def add(cls, **values):
        async with async_session_maker() as session:
            async with session.begin():
                new_product = cls.model(**values)
                session.add(new_product)
            await session.refresh(new_product)
            return new_product

    @classmethod
    async def delete_by_id(cls, id_line: int) -> int:
        async with async_session_maker() as session:
            async with session.begin():
                query = sqlalchemy_delete(cls.model).where(cls.model.id == id_line)
                result = await session.execute(query)
                return result.rowcount
