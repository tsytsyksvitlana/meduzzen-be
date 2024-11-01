import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.exceptions.users import (
    UserIdAlreadyExistsException,
    UserIdNotFoundException
)
from web_app.repositories.user_repository import UserRepository
from web_app.schemas.user import SignUpRequestModel, UserUpdateRequestModel
from web_app.services.users.user_service import UserService

pytestmark = pytest.mark.anyio


async def test_user_service_create_user(
    db_session: AsyncSession,
    create_test_users
):
    user_repository = UserRepository(session=db_session)
    user_service = UserService(user_repository=user_repository)

    user_data = SignUpRequestModel(
        first_name="Tom",
        last_name="Brown",
        email="unique.tom.brown@example.com",
        password="passDHHDJD/3"
    )

    created_user = await user_service.create_user(user_data)

    assert created_user.email == user_data.email
    assert created_user.first_name == user_data.first_name

    with pytest.raises(UserIdAlreadyExistsException):
        await user_service.create_user(user_data)


async def test_user_service_get_user_by_id(
    db_session: AsyncSession,
    create_test_users
):
    user_repository = UserRepository(session=db_session)
    user_service = UserService(user_repository=user_repository)

    user_from_fixture = create_test_users[0]
    fetched_user = await user_service.get_user_by_id(user_from_fixture.id)

    assert fetched_user.email == user_from_fixture.email

    with pytest.raises(UserIdNotFoundException):
        await user_service.get_user_by_id(-1)


async def test_user_service_update_user(
    db_session: AsyncSession,
    create_test_users
):
    user_repository = UserRepository(session=db_session)
    user_service = UserService(user_repository=user_repository)

    user_to_update = create_test_users[0]

    user_update = UserUpdateRequestModel(first_name="Emma", last_name="Brown")
    updated_user = await user_service.update_user(user_to_update.id, user_update)

    assert updated_user.first_name == "Emma"
    assert updated_user.last_name == "Brown"


async def test_user_service_delete_user(
    db_session: AsyncSession,
    create_test_users
):
    user_repository = UserRepository(session=db_session)
    user_service = UserService(user_repository=user_repository)

    user_to_delete = create_test_users[0]
    await user_service.delete_user(user_to_delete.id)

    with pytest.raises(UserIdNotFoundException):
        await user_service.get_user_by_id(user_to_delete.id)


async def test_user_service_get_user_by_email(
    db_session: AsyncSession,
    create_test_users
):
    user_repository = UserRepository(session=db_session)
    user_service = UserService(user_repository=user_repository)

    user_from_fixture = create_test_users[0]
    fetched_user = await user_service.get_user_by_id(user_from_fixture.id)

    assert fetched_user.email == user_from_fixture.email
