from fastapi import APIRouter, status

router = APIRouter()


@router.get("/")
async def healthcheck():
    return {
        "status_code": status.HTTP_200_OK,
        "detail": "ok",
        "result": "working"
    }
