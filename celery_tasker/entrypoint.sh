#!/bin/bash
set -e

echo "⏳ Ждём $DB_HOST:$DB_PORT ..."

if [[ -z "$DB_HOST" || -z "$DB_PORT" ]]; then
  echo "❌ Переменные DB_HOST и DB_PORT не заданы"
  exit 1
fi

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "✅ База готова."

echo "🚀 Запускаем Celery worker..."
celery -A app.main_celery worker --loglevel=info --pool=solo &

echo "🚀 Запускаем Celery beat..."
celery -A app.main_celery beat --loglevel=info &

echo "🚀 Запускаем Kafka consumer..."
python -m app.main_kafka_consumer &

wait
