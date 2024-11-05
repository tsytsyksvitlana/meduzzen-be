from fastapi import Request, status
from fastapi.responses import JSONResponse

from web_app.exceptions.application import ApplicationErrorException
from web_app.exceptions.auth import AuthorizationException
from web_app.exceptions.base import (
    ObjectAlreadyExistsException,
    ObjectNotFoundException
)
from web_app.exceptions.permission import PermissionDeniedException
from web_app.exceptions.validation import InvalidFieldException


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


async def handle_permission_denied_exception(
    request: Request, exc: PermissionDeniedException
):
    """
    Handles PermissionDeniedException and shows the error details.
    """
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.detail},
    )


async def handle_application_error_exception(
    request: Request, exc: ApplicationErrorException
):
    """
    Handles ApplicationErrorException and shows the error details.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.detail},
    )


async def handle_invalid_field_exception(
    request: Request, exc: InvalidFieldException
):
    """
    Handles InvalidFieldException and shows the error details.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.detail},
    )
