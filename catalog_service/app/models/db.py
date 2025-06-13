from sqlalchemy import ForeignKey, text, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db import Base, str_uniq, int_pk, str_null_true
from datetime import date

from app.models.mixins import BaseModelMixin


class Categories(BaseModelMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int_pk]
    name: Mapped[str]

    products: Mapped[list["Products"]] = relationship(
        back_populates="category", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"


class Products(Base):
    __tablename__ = "products"

    id: Mapped[int_pk]
    name: Mapped[str]
    price: Mapped[float]

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE")
    )

    category: Mapped["Categories"] = relationship(back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price})>"
