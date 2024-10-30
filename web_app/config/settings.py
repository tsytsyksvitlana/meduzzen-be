from pydantic_settings import BaseSettings

from web_app.config.auth_zero import AuthZeroConfig
from web_app.config.fastapi_config import FastAPIConfig
from web_app.config.jwt_config import JWTConfig
from web_app.config.postgres_config import PostgresSettings
from web_app.config.redis_config import RedisSettings


class Settings(BaseSettings):
    fastapi: FastAPIConfig = FastAPIConfig()
    postgres: PostgresSettings = PostgresSettings()
    redis: RedisSettings = RedisSettings()
    auth_jwt: JWTConfig = JWTConfig()
    auth_zero: AuthZeroConfig = AuthZeroConfig()


settings = Settings()
