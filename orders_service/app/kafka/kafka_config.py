from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class KafkaSettings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"
    KAFKA_SASL_MECHANISM: str | None = None
    KAFKA_USERNAME: str | None = None
    KAFKA_PASSWORD: str | None = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env", extra="ignore"
    )


settings = KafkaSettings()
