from sqlalchemy import update

from app.models.db import ExchangeRate, Orders
from app.db import session_maker


def save_exchange_rate(currency_pair: str, rate: float) -> None:
    with session_maker() as session:
        new_rate = ExchangeRate(currency=currency_pair, rate=rate)
        session.add(new_rate)
        session.commit()


def update_order_estimated_cost(order_id: int, estimated_cost: float) -> None:
    with session_maker() as session:
        session.execute(
            update(Orders)
            .where(Orders.id == order_id)
            .values(estimated_cost=estimated_cost)
        )
        session.commit()
