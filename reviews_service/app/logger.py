import logging
import sys
import json
from datetime import datetime, timezone
from loguru import logger

SERVICE_NAME = "reviews_service"


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger_opt = logger.opt(exception=record.exc_info, depth=6)
        logger_opt.log(level, record.getMessage())


def json_sink(message):
    record = message.record
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "level": record["level"].name,
        "service": SERVICE_NAME,
        "message": record["message"],
    }
    if record["exception"]:
        log_entry["exception"] = record["exception"].repr
    print(json.dumps(log_entry), flush=True)


def setup_logger():
    logger.remove()
    logger.add(json_sink, enqueue=True)
    logger.add(
        f"/logs/{SERVICE_NAME}.log",
        serialize=True,
        enqueue=True,
        rotation="10 MB",
        retention="7 days",
    )
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for log_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logging.getLogger(log_name).handlers = [InterceptHandler()]
