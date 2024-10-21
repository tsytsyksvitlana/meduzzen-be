import pytest
from fastapi.testclient import TestClient

from web_app.main import app


@pytest.fixture(scope="session")
def client():
    return TestClient(app)
