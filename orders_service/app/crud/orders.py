from typing import List
from decimal import Decimal

from app.db import async_session_maker
from app.models.db import Orders, OrderItems
from app.schemas.schemas import OrderUpdatePayload

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException


class OrderService:
    model = Orders

    @classmethod
    async def add(cls, user_id: str, items: List[dict], status_id: int = 0):
        async with async_session_maker() as session:
            async with session.begin():
                total_price = sum(
                    item["price_at_moment"] * item["quantity"] for item in items
                )

                new_order = cls.model(
                    user_id=user_id,
                    status_id=status_id,
                    total_price=total_price,
                )
                session.add(new_order)
                await session.flush()

                order_items = [
                    OrderItems(
                        order_id=new_order.id,
                        product_id=item["product_id"],
                        quantity=item["quantity"],
                        price_at_moment=item["price_at_moment"],
                    )
                    for item in items
                ]
                session.add_all(order_items)

            await session.refresh(new_order)
            return new_order

    @classmethod
    async def get_user_orders(cls, user_id: int):
        async with async_session_maker() as session:
            stmt = (
                select(cls.model)
                .options(selectinload(cls.model.items))  # получ содержимое заказа
                .where(cls.model.user_id == user_id)
            )
            result = await session.execute(stmt)
            orders = result.scalars().all()

            return orders

    @classmethod
    async def get_order(cls, order_id: int):
        async with async_session_maker() as session:
            stmt = (
                select(cls.model)
                .options(selectinload(cls.model.items))
                .where(cls.model.id == order_id)
            )
            result = await session.execute(stmt)
            order = result.scalars().first()

            return order

    @classmethod
    async def delete(cls, order_id: int):
        async with async_session_maker() as session:
            async with session.begin():
                stmt = delete(cls.model).where(cls.model.id == order_id)
                result = await session.execute(stmt)
                return result

    @classmethod
    async def update(cls, order_id: int, payload: OrderUpdatePayload):
        async with async_session_maker() as session:
            async with session.begin():
                # грузим заказ + товары
                stmt = (
                    select(cls.model)
                    .options(selectinload(cls.model.items))
                    .where(cls.model.id == order_id)
                )
                result = await session.execute(stmt)
                order = result.scalars().first()
                if not order:
                    return
                if payload.status_id is not None:
                    order.status_id = payload.status_id
                need_recalculate = False
                if payload.items:
                    for item_data in payload.items:
                        found = False
                        for item in order.items:
                            if item.id == item_data.item_id:
                                found = True
                                if item_data.quantity is not None:
                                    item.quantity = item_data.quantity
                                    need_recalculate = True
                                if item_data.price_at_moment is not None:
                                    item.price_at_moment = item_data.price_at_moment
                                    need_recalculate = True
                        if not found:
                            raise HTTPException(
                                status_code=404,
                                detail=f"Товар с id {item_data.item_id} не найден в заказе",
                            )
                # пересчитать total_price если надо
                if need_recalculate:
                    order.total_price = sum(
                        Decimal(item.quantity) * Decimal(item.price_at_moment)
                        for item in order.items
                    )
            await session.refresh(order)
            return order
