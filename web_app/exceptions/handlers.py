from fastapi import Request, status
from fastapi.responses import JSONResponse

from web_app.exceptions.auth import (
    AuthorizationException,
    TokenExpiredException
)
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
        content={
            "detail": f"{exc.object_type} with ID {exc.object_id} not found."
        },
    )


async def handle_object_already_exists_exception(
    request: Request, exc: ObjectAlreadyExistsException
):
    """
    Handles ObjectAlreadyExistsException and shows the error details.
    """
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": (
                f"{exc.object_type} with ID {exc.object_id} already exists."
            )
        },
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


async def handle_token_expired_exception(
    request: Request, exc: TokenExpiredException
):
    """
    Handles TokenExpiredException and shows the error details.
    """
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.detail},
    )
