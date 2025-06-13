#!/bin/bash
echo "⏳ Ждём $DB_HOST:$DB_PORT ..."

if [[ -z "$DB_HOST" || -z "$DB_PORT" ]]; then
  echo "❌ Переменные DB_HOST и DB_PORT не заданы"
  exit 1
fi

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "✅ База готова. Применяем миграции..."
alembic upgrade head

echo "🚀 Запускаем FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 4242