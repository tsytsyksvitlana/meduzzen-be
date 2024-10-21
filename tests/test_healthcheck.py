from fastapi import status


def test_read_healthcheck(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status_code": status.HTTP_200_OK,
        "detail": "ok",
        "result": "working",
    }
