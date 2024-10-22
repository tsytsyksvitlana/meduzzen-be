from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    REDIS_HOST: str
    REDIS_PORT: int
    SERVER_HOST: str
    SERVER_PORT: int
    RELOAD: bool

    echo: bool = True

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    @property
    def url(self):
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
