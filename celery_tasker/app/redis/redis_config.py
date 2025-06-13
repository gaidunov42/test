from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Redis_Settings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0
    REDIS_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env", extra="ignore"
    )


settings = Redis_Settings()


def get_redis_url():
    """
    Пример: redis://[:password]@localhost:6379/0
    """
    auth_part = f":{settings.REDIS_PASSWORD}@" if settings.REDIS_PASSWORD else ""
    return f"redis://{auth_part}{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"


def get_redis_url_for_broker():
    """
    Пример: redis://[:password]@localhost:6379/0
    """
    auth_part = f":{settings.REDIS_PASSWORD}@" if settings.REDIS_PASSWORD else ""
    return f"redis://{auth_part}{settings.REDIS_HOST}:{settings.REDIS_PORT}"
