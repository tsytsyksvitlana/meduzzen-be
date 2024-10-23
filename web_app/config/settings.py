from pydantic_settings import BaseSettings

from web_app.config.fastapi_config import FastAPIConfig
from web_app.config.postgres_config import PostgresSettings
from web_app.config.redis_config import RedisSettings


class Settings(BaseSettings):
    fastapi: FastAPIConfig = FastAPIConfig()
    postgres: PostgresSettings = PostgresSettings()
    redis: RedisSettings = RedisSettings()


settings = Settings()
