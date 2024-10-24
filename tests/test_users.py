# from datetime import datetime
# import pytest
# from fastapi.testclient import TestClient
# from sqlalchemy.ext.asyncio import AsyncSession
# from web_app.main import app
# from web_app.models import User
#
# pytestmark = pytest.mark.anyio
#
#
# @pytest.mark.asyncio
# async def test_get_users(client, db_session: AsyncSession):
#     """
#     Тест для перевірки роута get_users.
#     """
#     response = await client.get("/users")
#     assert response.status_code == 200
