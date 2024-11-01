from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class AuthZeroConfig(BaseSettings):
    AUTH0_DOMAIN: str
    AUTH0_AUDIENCE: str
    ALGORITHM: str = "RS256"

    model_config = ConfigDict(env_file=".env", extra="ignore")
