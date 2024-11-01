import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.schemas.user import SignUpRequestModel, UserUpdateRequestModel

pytestmark = pytest.mark.anyio


async def test_get_users(
    client: AsyncClient,
    db_session: AsyncSession,
    create_test_users
):
    response = await client.get("/users/")
    assert response.status_code == 200
    assert response.json()['total_count'] == len(create_test_users)
    assert all(
        user['email'] in [u.email for u in create_test_users]
        for user in response.json()['users']
    )


async def test_get_user(
    client: AsyncClient,
    db_session: AsyncSession,
    create_test_users
):
    user_id = create_test_users[0].id
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()['user']['email'] == create_test_users[0].email


async def test_get_user_not_found(
    client: AsyncClient,
    db_session: AsyncSession
):
    response = await client.get("/users/9999")
    assert response.status_code == 404


async def test_create_user(
    client: AsyncClient,
    db_session: AsyncSession
):
    user_data = SignUpRequestModel(
        first_name="Alice",
        last_name="Johnson",
        email="alice.johnson@example.com",
        password="securePassword123!"
    )
    response = await client.post("/auth/register", json=user_data.model_dump())
    assert response.status_code == 201
    assert response.json()['user']['email'] == user_data.email


async def test_create_user_duplicate(
    client: AsyncClient,
    db_session: AsyncSession,
    create_test_users
):
    user_data = SignUpRequestModel(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="anotherPassword456!"
    )
    response = await client.post("/auth/register", json=user_data.model_dump())
    assert response.status_code == 409


async def test_update_user(
    client: AsyncClient,
    db_session: AsyncSession,
    create_test_users
):
    user_id = create_test_users[0].id
    update_data = UserUpdateRequestModel(
        first_name="UpdatedName",
        last_name="UpdatedLastName"
    )
    response = await client.put(
        f"/users/{user_id}", json=update_data.model_dump()
    )
    assert response.status_code == 200
    assert response.json()['user']['first_name'] == update_data.first_name


async def test_update_user_not_found(
    client: AsyncClient,
    db_session: AsyncSession
):
    update_data = UserUpdateRequestModel(
        first_name="NonExistentName",
        last_name="NonExistentLastName"
    )
    response = await client.put("/users/9999", json=update_data.model_dump())
    assert response.status_code == 404


async def test_delete_user(
    client: AsyncClient,
    db_session: AsyncSession,
    create_test_users
):
    user_id = create_test_users[0].id
    response = await client.delete(f"/users/{user_id}")
    assert response.status_code == 204

    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 404


async def test_delete_user_not_found(
    client: AsyncClient,
    db_session: AsyncSession
):
    response = await client.delete("/users/9999")
    assert response.status_code == 404
