import json
import asyncio

from loguru import logger
from aiokafka import AIOKafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable, NodeNotReadyError

from app.kafka.kafka_config import settings


producer: AIOKafkaProducer | None = None


async def wait_kafka():
    for _ in range(50):
        try:
            admin = KafkaAdminClient(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                security_protocol=settings.KAFKA_SECURITY_PROTOCOL,
                sasl_mechanism=settings.KAFKA_SASL_MECHANISM,
                sasl_plain_username=settings.KAFKA_USERNAME,
                sasl_plain_password=settings.KAFKA_PASSWORD,
            )
            admin.close()
            logger.info("Kafka доступна")
            break
        except (NoBrokersAvailable, NodeNotReadyError):
            logger.info(f"Ожидание Kafka...")
            await asyncio.sleep(2)
    else:
        raise RuntimeError("Kafka недоступна после 50 попыток")


async def init_topic():
    try:
        admin = KafkaAdminClient(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            security_protocol=settings.KAFKA_SECURITY_PROTOCOL,
            sasl_mechanism=settings.KAFKA_SASL_MECHANISM,
            sasl_plain_username=settings.KAFKA_USERNAME,
            sasl_plain_password=settings.KAFKA_PASSWORD,
        )

        topic_list = admin.list_topics()
        if "review_events" not in topic_list:
            logger.info("Топик 'review_events' не найден, создаю...")
            admin.create_topics(
                [NewTopic(name="review_events", num_partitions=1, replication_factor=1)]
            )
            logger.info("Топик создан")
        else:
            logger.info("Топик 'review_events' уже существует")
    except TopicAlreadyExistsError:
        logger.info("Топик 'review_events' уже существует")
    finally:
        admin.close()


async def init_kafka_producer():
    global producer
    await wait_kafka()
    await init_topic()
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        security_protocol=settings.KAFKA_SECURITY_PROTOCOL,
        sasl_mechanism=settings.KAFKA_SASL_MECHANISM,
        sasl_plain_username=settings.KAFKA_USERNAME,
        sasl_plain_password=settings.KAFKA_PASSWORD,
    )
    await producer.start()


async def stop_kafka_producer():
    global producer
    if producer:
        await producer.stop()
        producer = None


async def produce_kafka_message(
    value: dict, topic: str = "review_events", key: str | None = None
):
    global producer

    if not producer:
        try:
            await init_kafka_producer()
        except Exception as e:
            raise RuntimeError("Не удалось инициализировать Kafka producer") from e

    if not producer:
        raise RuntimeError("Kafka producer не инициализирован")
    value["data"]["created_at"] = value["data"]["created_at"].isoformat()
    await producer.send_and_wait(
        topic=topic,
        value=json.dumps(value).encode("utf-8"),
        key=key.encode("utf-8") if key else None,
    )
