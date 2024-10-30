import logging
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import status
from httpx import AsyncClient
from jose import jwt

from web_app.config.settings import settings

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.anyio


async def test_get_current_user_with_valid_token(client: AsyncClient, create_test_users):
    login_response = await client.post(
        "/auth/login",
        json={"email": "john.doe@example.com", "password": "ggddHHHSDfd234/"},
    )

    if login_response.status_code != 200:
        logger.error(
            f"Login failed: {login_response.status_code}, {login_response.json()}"
        )

    access_token = login_response.json().get("access_token")
    assert access_token is not None, "Token should be returned on successful login"

    response = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
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
