import time
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.routes.reviews import reviews
from app.mongo.mongo_init import init_mongo_collections
from app.kafka.kafka_client import init_kafka_producer, stop_kafka_producer
from app.logger import setup_logger

setup_logger()

from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск сервера, проверка и создание коллекции в монге")
    await init_mongo_collections()
    logger.info("инициализация кафки")
    await init_kafka_producer()
    yield
    logger.info("Останока сервера")
    await stop_kafka_producer()


app = FastAPI(
    lifespan=lifespan
)  # lifespan - Можно написать код инициализации (что делать при старте и  что при остановке)


REQUEST_COUNT = Counter(
    "http_requests_total", "Total number of HTTP requests", ["method", "endpoint"]
)
REQUEST_LATENCY = Histogram(
    "latency_seconds", "Request latency in seconds", ["method", "endpoint"]
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    method = request.method
    endpoint = request.url.path

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

    return response


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


UPLOAD_DIR = Path("img")  # Что бы можно было отдавать файлы по ссылке
app.mount("/img", StaticFiles(directory=UPLOAD_DIR), name="img")


@app.get("/")
async def index():
    return {"Real": "Python"}


app.include_router(reviews)
