import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.anyio


async def test_get_users(client: AsyncClient, db_session: AsyncSession):
    response = await client.get("/users/")
    assert response.status_code == 200
