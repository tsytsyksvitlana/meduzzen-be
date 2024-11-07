import logging
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import status
from httpx import AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.config.settings import settings
from web_app.exceptions.auth import AuthorizationException
from web_app.models import User
from web_app.repositories.user_repository import UserRepository
from web_app.services.auth.auth_service import AuthService
from web_app.utils.password_manager import PasswordManager

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.anyio


async def test_get_current_user_with_valid_token(client: AsyncClient, create_test_users):
    login_response = await client.post(
        "/auth/login",
        json={"email": "john.doe@example.com", "password": "ggddHHHSDfd234/"},
    )

    if login_response.status_code != status.HTTP_200_OK:
        logger.error(
            f"Login failed: {login_response.status_code}, {login_response.json()}"
        )

    access_token = login_response.json().get("access_token")
    assert access_token is not None, "Token should be returned on successful login"

    response = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("user").get("email") == "john.doe@example.com"


async def test_get_current_user_with_expired_token(client: AsyncClient, create_test_users):
    user = create_test_users[0]
    expired_token = jwt.encode(
        {"email": user.email, "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
        settings.auth_jwt.SECRET_KEY,
        algorithm=settings.auth_jwt.ALGORITHM,
    )

    response = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Token has expired"}


async def test_change_password_success(
    db_session: AsyncSession, create_test_users
):
    user_repository = UserRepository(session=db_session)
    auth_service = AuthService(user_repository=user_repository)

    user = create_test_users[0]
    new_password = "NewSecurePassword123!"
    await auth_service.change_password(
        user, "ggddHHHSDfd234/", new_password
    )

    updated_user = await user_repository.get_obj_by_id(user.id)
    assert PasswordManager.verify_password(
        new_password, updated_user.password
    )


async def test_change_password_incorrect_old_password(
    db_session: AsyncSession, create_test_users
):
    user_repository = UserRepository(session=db_session)
    auth_service = AuthService(user_repository=user_repository)

    user = create_test_users[0]
    with pytest.raises(AuthorizationException, match="Uncorrect password."):
        await auth_service.change_password(
            user, "wWr0ngOldPass/word", "NewSecurePassword123/"
        )


async def test_set_password_success(db_session: AsyncSession):
    user_repository = UserRepository(session=db_session)
    auth_service = AuthService(user_repository=user_repository)

    user = User(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
    )
    await user_repository.create_obj(user)
    await user_repository.session.commit()

    password_to_set = "PasswordToSet123!"
    await auth_service.set_password(user, password_to_set)

    updated_user = await user_repository.get_obj_by_id(user.id)
    assert PasswordManager.verify_password(password_to_set, updated_user.password)


async def test_set_password_when_password_exists(db_session: AsyncSession, create_test_users):
    user_repository = UserRepository(session=db_session)
    auth_service = AuthService(user_repository=user_repository)

    user = create_test_users[0]
    with pytest.raises(AuthorizationException, match="User already has a password."):
        await auth_service.set_password(user, "NewPassword123!")
