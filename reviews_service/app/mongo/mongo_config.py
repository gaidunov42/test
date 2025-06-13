from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class MongoSettings(BaseSettings):
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_AUTH_SOURCE: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",  # 2 уровня вверх
        extra="ignore",
    )


settings = MongoSettings()


def get_mongo_url():
    auth_part = (
        f"{settings.MONGO_USER}:{settings.MONGO_PASSWORD}@"
        if settings.MONGO_USER and settings.MONGO_PASSWORD
        else ""
    )
    query_part = (
        f"?authSource={settings.MONGO_AUTH_SOURCE}" if settings.MONGO_USER else ""
    )
    return f"mongodb://{auth_part}{settings.MONGO_HOST}:{settings.MONGO_PORT}/{settings.MONGO_DB}{query_part}"
