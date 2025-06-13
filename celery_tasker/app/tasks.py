import requests
from loguru import logger

from app.main_celery import celery
from app.services.cache_service import cash
from app.crud.rate import save_exchange_rate


@celery.task
def get_usd_rub_rate():
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
        response.raise_for_status()
        data = response.json()
        usd = data["Valute"]["USD"]["Value"]
        cash.set_value("usd_rub_rate", usd)
        save_exchange_rate(currency_pair="USD/RUB", rate=usd)
        logger.info(f"[✓] Updated USD/RUB rate: {usd}")
    except Exception as e:
        logger.error(f"[!] Failed to update rate: {e}")
