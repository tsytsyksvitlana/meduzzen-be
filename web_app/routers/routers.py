from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/")
async def healthcheck():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }
