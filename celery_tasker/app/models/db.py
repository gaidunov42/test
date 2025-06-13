from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from app.db import Base, int_pk


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency = Column(String(10), nullable=False)
    rate = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<ExchangeRate({self.currency_pair}={self.rate} @ {self.timestamp})>"


class Orders(Base):
    __tablename__ = "orders"

    id: Mapped[int_pk]
    estimated_cost: Mapped[float] = mapped_column(Float)
