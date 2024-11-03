import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models import User
from web_app.repositories.user_repository import UserRepository
from web_app.utils.password_manager import PasswordManager

pytestmark = pytest.mark.anyio


async def test_create_user(db_session: AsyncSession):
    user_repository = UserRepository(session=db_session)
    user_data = User(
        first_name="Alice",
        last_name="Johnson",
        email="alice.johnson@example.com",
        password=PasswordManager.hash_password("HDBgfed562347/")
    )

    created_user = await user_repository.create_obj(user_data)
    await user_repository.session.commit()

    assert created_user.id is not None
    assert created_user.email == user_data.email


async def test_get_user_by_id(db_session: AsyncSession, create_test_users):
    user_repository = UserRepository(session=db_session)
    user_data = create_test_users[0]

    fetched_user = await user_repository.get_obj_by_id(user_data.id)

    assert fetched_user is not None
    assert fetched_user.id == user_data.id
    assert fetched_user.email == user_data.email


async def test_update_user(db_session: AsyncSession, create_test_users):
    user_repository = UserRepository(session=db_session)
    user_data = create_test_users[0]

    user_data.first_name = "UpdatedName"
    updated_user = await user_repository.update_obj(user_data)
    await user_repository.session.commit()

    assert updated_user.first_name == "UpdatedName"


async def test_delete_user(db_session: AsyncSession, create_test_users):
    user_repository = UserRepository(session=db_session)
    user_data = create_test_users[0]

    deleted_user = await user_repository.delete_obj(user_data.id)
    await user_repository.session.commit()

    assert deleted_user.id == user_data.id
    assert await user_repository.get_obj_by_id(user_data.id) is None


async def test_get_user_by_email(db_session: AsyncSession, create_test_users):
    user_repository = UserRepository(session=db_session)
    user_data = create_test_users[0]

    fetched_user = await user_repository.get_user_by_email(user_data.email)

    assert fetched_user is not None
    assert fetched_user.email == user_data.email
