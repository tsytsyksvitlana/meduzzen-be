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
from web_app.models import Company, CompanyMembership, User
from web_app.models.base import Base
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.repositories.question_repository import QuestionRepository
from web_app.repositories.quiz_repository import QuizRepository
from web_app.schemas.quiz import AnswerCreate, QuestionCreate, QuizCreate
from web_app.services.quizzes.quiz_service import QuizService
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
        }
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
async def create_test_companies(db_session: AsyncSession):
    companies_data = [
        {
            "name": "Test Company 1",
            "description": "Description for Test Company 1.",
            "is_visible": True,
            "address": "100 Test St.",
            "contact_email": "contact@testcompany1.com",
            "phone_number": "1112223333",
        },
        {
            "name": "Test Company 2",
            "description": "Description for Test Company 2.",
            "is_visible": False,
            "address": "200 Test Ave.",
            "contact_email": "contact@testcompany2.com",
            "phone_number": "4445556666",
        }
    ]
    for data in companies_data:
        new_company = Company(**data)
        db_session.add(new_company)
    await db_session.commit()

    result = await db_session.execute(select(Company))
    created_companies = result.scalars().all()

    return created_companies


@pytest.fixture
async def token_first_user(client: AsyncClient, create_test_users):
    user = create_test_users[0]
    login_response = await client.post(
        "/auth/login",
        json={"email": user.email, "password": "ggddHHHSDfd234/"},
    )
    access_token = login_response.json().get("access_token")
    return access_token


@pytest.fixture
async def create_test_quizzes(db_session: AsyncSession, create_test_users, create_test_companies):
    create_test_company = create_test_companies[0]
    user = create_test_users[0]
    company_id = create_test_company.id

    company_membership = CompanyMembership(
        company_id=company_id,
        user_id=user.id,
        role="Owner",
    )
    db_session.add(company_membership)
    await db_session.commit()

    quiz_data_1 = QuizCreate(
        title="General Knowledge Quiz",
        description="Test your knowledge",
        participation_frequency=10,
        company_id=company_id,
        questions=[
            QuestionCreate(
                title="What is the capital of France?",
                answers=[
                    AnswerCreate(text="Paris", is_correct=True),
                    AnswerCreate(text="London", is_correct=False)
                ]
            ),
            QuestionCreate(
                title="What is 2 + 2?",
                answers=[
                    AnswerCreate(text="4", is_correct=True),
                    AnswerCreate(text="5", is_correct=False)
                ]
            ),
            QuestionCreate(
                title="when is independence day of Ukraine",
                answers=[
                    AnswerCreate(text="24 August", is_correct=True),
                    AnswerCreate(text="28 July", is_correct=False)
                ]
            )
        ]
    )

    quiz_data_2 = QuizCreate(
        title="Math Quiz",
        description="Test your math skills",
        participation_frequency=5,
        company_id=company_id,
        questions=[
            QuestionCreate(
                title="What is 3 + 3?",
                answers=[
                    AnswerCreate(text="6", is_correct=True),
                    AnswerCreate(text="7", is_correct=False)
                ]
            ),
            QuestionCreate(
                title="What is 5 + 5?",
                answers=[
                    AnswerCreate(text="10", is_correct=True),
                    AnswerCreate(text="11", is_correct=False)
                ]
            )
        ]
    )
    quiz_repository = QuizRepository(session=db_session)
    question_repository = QuestionRepository(session=db_session)
    company_repository = CompanyRepository(session=db_session)
    membership_repository = CompanyMembershipRepository(session=db_session)

    quiz_service = QuizService(
        quiz_repository=quiz_repository,
        question_repository=question_repository,
        company_repository=company_repository,
        membership_repository=membership_repository
    )

    created_quiz_1 = await quiz_service.create_quiz(quiz_data_1, current_user=user)
    created_quiz_2 = await quiz_service.create_quiz(quiz_data_2, current_user=user)

    return [created_quiz_1, created_quiz_2]


@pytest.fixture(scope="function")
def anyio_backend():
    return "asyncio"
