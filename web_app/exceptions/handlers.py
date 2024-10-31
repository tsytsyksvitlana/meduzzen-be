from fastapi import Request, status
from fastapi.responses import JSONResponse

from web_app.exceptions.auth import AuthorizationException
from web_app.exceptions.base import (
    ObjectAlreadyExistsException,
    ObjectNotFoundException
)


async def handle_object_not_found_exception(
    request: Request, exc: ObjectNotFoundException
):
    """
    Handles ObjectNotFoundException and shows the error details.
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def handle_object_already_exists_exception(
    request: Request, exc: ObjectAlreadyExistsException
):
    """
    Handles ObjectAlreadyExistsException and shows the error details.
    """
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


async def handle_authorization_exception(
    request: Request, exc: AuthorizationException
):
    """
    Handles AuthorizationException and shows the error details.
    """
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.detail},
    )
