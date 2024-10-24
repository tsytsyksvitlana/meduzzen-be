from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    echo: bool = True

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def update_url(self, new_url: str):
        """
        Function parses URL and updates the connection details accordingly.
        """
        _user, _password, _host, _port, _db_name = self._parse_url(new_url)
        self.POSTGRES_USER = _user
        self.POSTGRES_PASSWORD = _password
        self.POSTGRES_HOST = _host
        self.POSTGRES_PORT = _port
        self.POSTGRES_DB = _db_name

    def _parse_url(self, url: str):
        """
        Function parses url into components
        """
        url_parts = url.split("@")
        credentials, host_info = url_parts[0].split("://")[1], url_parts[1]
        user, password = credentials.split(":")
        host, port_name = host_info.split(":")
        port, name = port_name.split("/")

        return user, password, host, port, name


class TestPostgresSettings(PostgresSettings):
    class Config:
        env_file = ".env.test"
