from fastapi import Request, status, APIRouter
from fastapi.responses import JSONResponse

from web_app.exceptions.auth import (
    AuthorizationException,
    TokenExpiredException
)
from web_app.exceptions.base import ObjectAlreadyExistsException
from web_app.exceptions.users import (
    UserEmailNotFoundException,
    UserIdNotFoundException
)


async def handle_user_id_not_found_exception(
    request: Request, exc: UserIdNotFoundException
):
    """
    Handles UserIdNotFoundException and shows the error details.
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": f"User with ID {exc.object_id} not found."
        },
    )


async def handle_user_email_not_found_exception(
    request: Request, exc: UserEmailNotFoundException
):
    """
    Handles UserEmailNotFoundException and shows the error details.
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": f"User with email {exc.object_id} not found."
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


async def handle_exception(request: Request, exc) -> JSONResponse:
    handlers = {
        UserIdNotFoundException: handle_user_id_not_found_exception,
        UserEmailNotFoundException: handle_user_email_not_found_exception,
        ObjectAlreadyExistsException: handle_object_already_exists_exception,
        AuthorizationException: handle_authorization_exception,
        TokenExpiredException: handle_token_expired_exception,
    }

    handler = handlers.get(type(exc))

    if handler:
        return await handler(request, exc)
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred."}
        )
