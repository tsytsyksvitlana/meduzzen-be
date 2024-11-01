import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from web_app.config.settings import settings
from web_app.db.redis_helper import redis_helper
from web_app.exceptions.auth import AuthorizationException
from web_app.exceptions.base import (
    ObjectAlreadyExistsException,
    ObjectNotFoundException
)
from web_app.exceptions.handlers import (
    handle_authorization_exception,
    handle_object_already_exists_exception,
    handle_object_not_found_exception
)
from web_app.logging.logger import setup_logger
from web_app.routers.auth import router as auth_router
from web_app.routers.healthcheck import router as router
from web_app.routers.users import router as users_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    setup_logger(settings.fastapi.ENV_MODE)

    await redis_helper.redis.ping()
    logger.info("Redis connected.")

    yield

    await redis_helper.close()
    logger.info("Redis connection closed.")


app = FastAPI(lifespan=lifespan)

auth_header = HTTPBearer()
app.include_router(router)
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])

origins = [
    f"http://{settings.fastapi.SERVER_HOST}:{settings.fastapi.SERVER_PORT}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """
    Handles HTTP exceptions and logs the error details.
    Returns the appropriate response based on the HTTP error.
    """
    logger.error(f"HTTP error: {exc.detail}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


app.add_exception_handler(
    ObjectNotFoundException, handle_object_not_found_exception
)
app.add_exception_handler(
    ObjectAlreadyExistsException, handle_object_already_exists_exception
)
app.add_exception_handler(
    AuthorizationException, handle_authorization_exception
)


if __name__ == "__main__":
    uvicorn.run(
        "web_app.main:app",
        host=settings.fastapi.SERVER_HOST,
        port=settings.fastapi.SERVER_PORT,
        reload=settings.fastapi.SERVER_RELOAD,
    )
