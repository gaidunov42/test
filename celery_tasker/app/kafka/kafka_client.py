import time
import json

from confluent_kafka import Consumer, KafkaException, KafkaError
from loguru import logger

from app.kafka.kafka_config import settings

consumer: Consumer | None = None


def init_kafka_consumer(group_id: str, topic: str):
    global consumer
    config = {
        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "security.protocol": settings.KAFKA_SECURITY_PROTOCOL,
        # "sasl.mechanism": settings.KAFKA_SASL_MECHANISM,
        "sasl.username": settings.KAFKA_USERNAME,
        "sasl.password": settings.KAFKA_PASSWORD,
        "group.id": group_id,
        "auto.offset.reset": "earliest",
    }

    consumer = Consumer(config)
    logger.info(f"Ожидание появления Kafka-топика '{topic}'...")
    while True:
        try:
            metadata = consumer.list_topics(timeout=5)
            if topic in metadata.topics:
                logger.info(f"Топик '{topic}' найден. Подписываемся...")
                break
            else:
                logger.info(
                    f"Топик '{topic}' пока не найден. Повтор через 3 секунды..."
                )
        except KafkaException as e:
            logger.info(f"Kafka недоступна: {e}. Повтор через 3 секунды...")

        time.sleep(3)

    consumer.subscribe([topic])


def consume_messages(handler: callable):
    global consumer
    if not consumer:
        raise RuntimeError("Kafka consumer не инициализирован")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    raise KafkaException(msg.error())
                continue

            value = json.loads(msg.value().decode("utf-8"))
            handler(value)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
