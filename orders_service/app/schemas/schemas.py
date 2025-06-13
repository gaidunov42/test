from uuid import UUID
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Количество товара должно быть больше 0")
    price_at_moment: Decimal = Field(gt=0, description="Цена товара на момент заказа")

    class Config:
        from_attributes = True


class NewOrderPayload(BaseModel):
    user_id: UUID
    status_id: int
    items: List[OrderItemCreate]

    class Config:
        from_attributes = True


class OrderCreateResponse(BaseModel):
    message: str
    order_id: int
    total_price: Decimal

    class Config:
        from_attributes = True


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price_at_moment: Decimal

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    total_price: Decimal
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


class UserOrdersResponse(BaseModel):
    orders: List[OrderResponse]

    class Config:
        from_attributes = True


class OrderItemUpdatePayload(BaseModel):
    item_id: int
    quantity: Optional[int] = None
    price_at_moment: Optional[Decimal] = None

    class Config:
        from_attributes = True


class OrderUpdatePayload(BaseModel):
    status_id: Optional[int] = None
    items: Optional[List[OrderItemUpdatePayload]] = None

    class Config:
        from_attributes = True
