import logging

import pytest
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from tests.config.postgres_config import test_postgres_settings
from web_app.config.settings import settings
from web_app.db.postgres_helper import postgres_helper
from web_app.main import app
from web_app.models import User
from web_app.models.base import Base
from web_app.utils.password_manager import PasswordManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
async def client() -> AsyncClient:
    logger.info("Creating HTTP client...")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url=f"http://{settings.fastapi.SERVER_HOST}:"
                 f"{settings.fastapi.SERVER_PORT}",
    ) as ac:
        yield ac
    logger.info("HTTP client closed.")


@pytest.fixture(scope="function")
async def setup_test_db_and_teardown():
    logger.info("Setting up the test database...")

    postgres_helper.engine = create_async_engine(
        test_postgres_settings.url,
        echo=test_postgres_settings.echo
    )
    postgres_helper.session_factory = async_sessionmaker(
        bind=postgres_helper.engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    async with postgres_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created.")

    alembic_cfg = Config("web_app/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_postgres_settings.url)
    alembic_cfg.set_main_option("script_location", "web_app/migrations")

    yield postgres_helper.session_factory

    logger.info("Tearing down the test database...")
    async with postgres_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await postgres_helper.engine.dispose()
    logger.info("Test database dropped.")


@pytest.fixture(scope="function")
async def db_session(setup_test_db_and_teardown) -> AsyncSession:
    async_session_factory = setup_test_db_and_teardown
    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def create_test_users(db_session: AsyncSession):
    users_data = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "ggddHHHSDfd234/",
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "password": "vdsfhDFDF/934",
        },
    ]
    for data in users_data:
        hashed_password = PasswordManager.hash_password(data["password"])
        new_user = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=hashed_password,
        )
        db_session.add(new_user)
    await db_session.commit()

    result = await db_session.execute(select(User))
    created_users = result.scalars().all()

    return created_users


@pytest.fixture(scope="function")
def anyio_backend():
    return "asyncio"
