from celery import Celery
from app.redis.redis_config import get_redis_url_for_broker
from app.logger import setup_logger


setup_logger()

redis_url = get_redis_url_for_broker()

celery = Celery("currency_app", broker=f"{redis_url}/1", backend=f"{redis_url}/2")

celery.conf.beat_schedule = {
    "get-usd-rate-every-minute": {
        "task": "app.tasks.get_usd_rub_rate",
        "schedule": 60.0,
        "args": [],
    },
}
celery.conf.timezone = "UTC"

celery.conf.beat_scheduler = "celery.beat:Scheduler"

celery.autodiscover_tasks(["app"])


# celery -A app.main_celery worker --loglevel=info --pool=solo
# celery -A app.main_celery beat --loglevel=info
