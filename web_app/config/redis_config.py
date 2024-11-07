from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: str
    EXPIRE_SECONDS: int = 60 * 60 * 48
