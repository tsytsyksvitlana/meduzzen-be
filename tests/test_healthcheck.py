import pytest
from fastapi import status
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_read_healthcheck(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status_code": status.HTTP_200_OK,
        "detail": "ok",
        "result": "working",
    }
