from typing import Optional
from pydantic import BaseModel, Field


class ProductsPayload(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None


class CategoryPayload(BaseModel):
    name: str


class SCategory(BaseModel):
    id: int
    name: str = Field(
        ..., min_length=1, max_length=500, description="Наименование категории"
    )

    class Config:
        orm_mode = True


class SProduct(BaseModel):
    id: int
    name: str = Field(
        ..., min_length=1, max_length=500, description="Наименование позиции"
    )
    price: float = Field(..., description="Стоимость")
    category: SCategory

    class Config:
        orm_mode = True
