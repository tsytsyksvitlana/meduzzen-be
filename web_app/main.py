import logging
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from web_app.config.settings import settings
from web_app.db.redis_helper import redis_helper
from web_app.exceptions.application import (
    ApplicationErrorException,
    BadRequestException
)
from web_app.exceptions.auth import AuthorizationException
from web_app.exceptions.base import (
    ObjectAlreadyExistsException,
    ObjectNotFoundException
)
from web_app.exceptions.data import DataNotFoundException
from web_app.exceptions.handlers import (
    handle_application_error_exception,
    handle_authorization_exception,
    handle_bad_request_exception,
    handle_data_request_exception,
    handle_invalid_field_exception,
    handle_object_already_exists_exception,
    handle_object_not_found_exception,
    handle_permission_denied_exception
)
from web_app.exceptions.permission import PermissionDeniedException
from web_app.exceptions.validation import InvalidFieldException
from web_app.logging.logger import setup_logger
from web_app.routers.auth import router as auth_router
from web_app.routers.companies import router as companies_router
from web_app.routers.export import router as export_router
from web_app.routers.healthcheck import router as router
from web_app.routers.invitations import router as invitations_router
from web_app.routers.join_requests import router as join_requests_router
from web_app.routers.notifications import router as notifications_router
from web_app.routers.quiz_results import router as quiz_results_router
from web_app.routers.quizzes import router as quizzes_router
from web_app.routers.users import router as users_router
from web_app.tasks.notifications import task_notify_inactive_users

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    setup_logger(settings.fastapi.ENV_MODE)

    await redis_helper.redis.ping()
    logger.info("Redis connected.")

    scheduler.start()
    logger.info("Scheduler started.")
    scheduler.add_job(task_notify_inactive_users, CronTrigger(hour=0, minute=0))

    yield

    scheduler.shutdown()
    logger.info("Scheduler shutdown.")

    await redis_helper.close()
    logger.info("Redis connection closed.")


app = FastAPI(lifespan=lifespan)

auth_header = HTTPBearer()
app.include_router(router)
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(companies_router, prefix="/company", tags=["companies"])
app.include_router(invitations_router, prefix="/invitations", tags=["invitations"])
app.include_router(join_requests_router, tags=["join_requests"])
app.include_router(quizzes_router, prefix="/quizzes", tags=["quizzes"])
app.include_router(export_router, tags=["export_data"])
app.include_router(quiz_results_router, tags=["quiz_results"])
app.include_router(notifications_router, prefix="/notifications", tags=["notifications"])

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
app.add_exception_handler(
    PermissionDeniedException, handle_permission_denied_exception
)
app.add_exception_handler(
    ApplicationErrorException, handle_application_error_exception
)
app.add_exception_handler(
    InvalidFieldException, handle_invalid_field_exception
)
app.add_exception_handler(
    BadRequestException, handle_bad_request_exception
)
app.add_exception_handler(
    DataNotFoundException, handle_data_request_exception
)


if __name__ == "__main__":
    uvicorn.run(
        "web_app.main:app",
        host=settings.fastapi.SERVER_HOST,
        port=settings.fastapi.SERVER_PORT,
        reload=settings.fastapi.SERVER_RELOAD,
    )
