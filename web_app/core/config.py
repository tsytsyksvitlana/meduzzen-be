from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class FastAPIConfig(BaseSettings):
    server_host: str = "localhost"
    server_port: int = 8000
    reload: bool = True

    model_config = ConfigDict()


config = FastAPIConfig()
