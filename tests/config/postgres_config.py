from pydantic import ConfigDict

from web_app.config.postgres_config import PostgresSettings


class TestPostgresSettings(PostgresSettings):
    model_config = ConfigDict(env_file=".env.test")


test_postgres_settings = TestPostgresSettings()
