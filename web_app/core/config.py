import os
from pydantic_settings import BaseSettings


class FastAPIConfig(BaseSettings):
    server_host: str = os.getenv('SERVER_HOST', 'localhost')
    server_port: int = int(os.getenv('SERVER_PORT', 8000))
    reload: bool = os.getenv('RELOAD', True)


config = FastAPIConfig()
