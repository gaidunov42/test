from app.kafka.kafka_client import init_kafka_consumer, consume_messages
from app.services.cache_service import cash
from app.crud.rate import update_order_estimated_cost
from app.logger import setup_logger

setup_logger()

from loguru import logger


def handle_product_event(event):
    logger.info(f"Received event: {event}")
    if event["event"] != "ORDER_CREATED":
        return
    usd_rub_rate = cash.get_value("usd_rub_rate")
    order_id = event["order_id"]
    estimated_cost = float(usd_rub_rate) * float(event["price"])
    update_order_estimated_cost(order_id, estimated_cost)


init_kafka_consumer(group_id="consumer", topic="order_events")
consume_messages(handler=handle_product_event)
