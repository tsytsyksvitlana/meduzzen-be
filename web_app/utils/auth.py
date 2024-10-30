import logging
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.config.settings import settings
from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.exceptions.auth import (
    AuthorizationException,
    TokenExpiredException
)
from web_app.repositories.user_repository import UserRepository
from web_app.services.users.user_service import UserService
from web_app.utils.token_decoders.auth_zero_decoder import AuthZeroTokenDecoder
from web_app.utils.token_decoders.custom_token_decoder import (
    CustomTokenDecoder
)

logger = logging.getLogger(__name__)


def create_access_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.auth_jwt.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.auth_jwt.SECRET_KEY,
        algorithm=settings.auth_jwt.ALGORITHM
    )


async def get_user_service(
    session: AsyncSession = Depends(pg_helper.session_getter)
) -> UserService:
    return UserService(user_repository=UserRepository(session))


async def get_current_user(
        authorization: str = Header(None),
        user_service: UserService = Depends(get_user_service)
):
    if not authorization:
        raise AuthorizationException(detail="Authorization header missing")

    token_type, _, token = authorization.partition(" ")
    if token_type.lower() != "bearer" or not token:
        raise AuthorizationException(detail="Invalid authorization header")

    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg")

        if alg == "HS256":
            decoder = CustomTokenDecoder()
        elif alg == "RS256":
            decoder = AuthZeroTokenDecoder()
        else:
            raise AuthorizationException(detail="Unsupported algorithm")

        payload = decoder.decode(token)

        if email := payload.get("email") or payload.get("sub"):
            await user_service.create_user_by_email(email)

        logger.info(f"Authenticated user: {email}")
        return {"email": email}

    except JWTError as e:
        logger.error(f"JWT error: {str(e)}")
        raise TokenExpiredException()
    except Exception as e:
        logger.error(f"Error decoding token: {str(e)}")
        raise AuthorizationException(detail="Invalid token")
