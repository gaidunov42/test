from motor.motor_asyncio import AsyncIOMotorClient
from app.mongo.mongo_config import get_mongo_url, settings


class Mongo:
    def __init__(self):
        self._client: AsyncIOMotorClient | None = None
        self._db = None

    async def __aenter__(self):
        self._client = AsyncIOMotorClient(get_mongo_url())
        self._db = self._client[settings.MONGO_DB]
        return self._db

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._client.close()
