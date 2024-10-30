import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from web_app.config.settings import settings
from web_app.db.redis_helper import redis_helper
from web_app.exceptions.auth import (
    AuthorizationException,
    TokenExpiredException
)
from web_app.exceptions.base import ObjectAlreadyExistsException
from web_app.exceptions.handlers import (
    handle_authorization_exception,
    handle_object_already_exists_exception,
    handle_token_expired_exception,
    handle_user_email_not_found_exception,
    handle_user_id_not_found_exception
)
from web_app.exceptions.users import (
    UserEmailNotFoundException,
    UserIdNotFoundException
)
from web_app.routers.auth import router as auth_router
from web_app.routers.healthcheck import router as router
from web_app.routers.users import router as users_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    # setup_logger(settings.fastapi.ENV_MODE)

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


@app.exception_handler(Exception)
async def exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handles unhandled exceptions and logs the error details.
    Returns a 500 response with an error message.
    """
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
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


@app.exception_handler(UserIdNotFoundException)
async def user_id_not_found_handler(
    request: Request,
    exc: UserIdNotFoundException
):
    return await handle_user_id_not_found_exception(request, exc)


@app.exception_handler(UserEmailNotFoundException)
async def user_email_not_found_handler(
    request: Request,
    exc: UserEmailNotFoundException
):
    return await handle_user_email_not_found_exception(request, exc)


@app.exception_handler(ObjectAlreadyExistsException)
async def object_already_exists_handler(
    request: Request,
    exc: ObjectAlreadyExistsException
):
    return await handle_object_already_exists_exception(request, exc)


@app.exception_handler(AuthorizationException)
async def auth_exception_handler(
    request: Request,
    exc: AuthorizationException
):
    return await handle_authorization_exception(request, exc)


@app.exception_handler(TokenExpiredException)
async def auth_token_handler(
    request: Request,
    exc: TokenExpiredException
):
    return await handle_token_expired_exception(request, exc)


if __name__ == "__main__":
    uvicorn.run(
        "web_app.main:app",
        host=settings.fastapi.SERVER_HOST,
        port=settings.fastapi.SERVER_PORT,
        reload=settings.fastapi.SERVER_RELOAD,
    )
