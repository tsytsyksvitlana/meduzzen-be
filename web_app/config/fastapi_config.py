from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class FastAPIConfig(BaseSettings):
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 8000
    SERVER_RELOAD: bool = True

    model_config = ConfigDict()
