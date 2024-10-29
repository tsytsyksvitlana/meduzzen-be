import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, status
from jose import JWTError, jwt

from web_app.config.settings import settings
from web_app.exceptions.auth import (
    AuthorizationException,
    TokenExpiredException
)
from web_app.exceptions.base import ObjectNotFoundException
from web_app.routers.users import get_user_service
from web_app.schemas.token import Token
from web_app.schemas.user import (
    SignInRequestModel,
    SignUpRequestModel,
    UserDetailResponse,
    UserSchema
)
from web_app.services.users.user_service import UserService
from web_app.utils.password_manager import PasswordManager

router = APIRouter()
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


def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise AuthorizationException(detail="Authorization header missing")

    token_type, _, token = authorization.partition(" ")
    if token_type.lower() != "bearer" or not token:
        raise AuthorizationException(detail="Invalid authorization header")

    try:
        payload = jwt.decode(
            token,
            settings.auth_jwt.SECRET_KEY,
            algorithms=[settings.auth_jwt.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise AuthorizationException(detail="Invalid token")
        return {"email": email}
    except JWTError:
        raise TokenExpiredException()


@router.post(
    "/register", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: SignUpRequestModel,
    user_service: UserService = Depends(get_user_service)
) -> UserDetailResponse:
    """
    Create a new user in the database.
    """
    user = await user_service.create_user(user)
    logger.info(f"Created new user with ID {user.id}.")
    user_schema = UserSchema(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_activity_at=user.last_activity_at
    )
    return UserDetailResponse(user=user_schema)


@router.post("/login", response_model=Token)
async def login(
    user: SignInRequestModel,
    user_service: UserService = Depends(get_user_service)
):
    db_user = await user_service.get_user_by_email(user.email)
    if PasswordManager.verify_password(user.password, db_user.password):
        access_token = create_access_token(data={"sub": user.email})
        logger.info(f"User {user.email} logged in successfully")
        return {"access_token": access_token, "token_type": "Bearer"}
    logger.warning(f"Invalid login attempt for user: {user.email}")
    raise AuthorizationException(detail="Invalid username or password")


@router.get("/me", response_model=UserDetailResponse)
async def read_users_me(
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    email = current_user.get("email")
    db_user = await user_service.get_user_by_email(email)
    if not db_user:
        logger.warning(f"User with email {email} not found")
        raise ObjectNotFoundException("User", email)
    logger.info(f"User profile retrieved for {email}")
    user_schema = UserSchema(
        id=db_user.id,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        email=db_user.email,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at,
        last_activity_at=db_user.last_activity_at
    )
    return UserDetailResponse(user=user_schema)
