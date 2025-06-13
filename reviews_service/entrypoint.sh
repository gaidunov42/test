#!/bin/bash

echo "⏳ Ждём MongoDB на $MONGO_HOST:$MONGO_PORT ..."

if [[ -z "$MONGO_HOST" || -z "$MONGO_PORT" ]]; then
  echo "❌ Переменные MONGO_HOST и MONGO_PORT не заданы"
  exit 1
fi

while ! nc -z "$MONGO_HOST" "$MONGO_PORT"; do
  sleep 1
done

echo "✅ Mongo готов. Запускаем FastAPI..."

exec uvicorn app.main:app --host 0.0.0.0 --port 8000