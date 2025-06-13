import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from app.db import Base, int_pk, str_uniq


class OrderStatuses(Base):
    __tablename__ = "order_statuses"

    id: Mapped[int_pk]
    name: Mapped[str_uniq]

    orders: Mapped[list["Orders"]] = relationship(
        back_populates="status",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<OrderStatus(id={self.id}, name={self.name})>"


class Orders(Base):
    __tablename__ = "orders"

    id: Mapped[int_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status_id: Mapped[int] = mapped_column(
        ForeignKey("order_statuses.id", ondelete="SET NULL"), nullable=True
    )
    estimated_cost: Mapped[float] = mapped_column(Float)
    total_price: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    status: Mapped["OrderStatuses"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItems"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, total_price={self.total_price})>"


class OrderItems(Base):
    __tablename__ = "order_items"

    id: Mapped[int_pk]
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[int]
    quantity: Mapped[int]
    price_at_moment: Mapped[float] = mapped_column(Float)

    order: Mapped["Orders"] = relationship(back_populates="items")

    def __repr__(self):
        return (
            f"<OrderItem(id={self.id}, order_id={self.order_id}, "
            f"product_id={self.product_id}, quantity={self.quantity}, "
            f"price_at_moment={self.price_at_moment})>"
        )
