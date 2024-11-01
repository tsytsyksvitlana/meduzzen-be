import logging

from fastapi import APIRouter, Depends, status

from web_app.models import User
from web_app.routers.users import get_user_service
from web_app.schemas.token import Token
from web_app.schemas.user import (
    SignInRequestModel,
    SignUpRequestModel,
    UserDetailResponse,
    UserSchema
)
from web_app.services.auth.auth_service import AuthService, get_auth_service
from web_app.services.users.user_service import UserService
from web_app.utils.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/register",
    response_model=UserDetailResponse,
    status_code=status.HTTP_201_CREATED
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
    auth_service: AuthService = Depends(get_auth_service)
):
    access_token = await auth_service.authenticate_user(user)
    logger.info(f"User {user.email} logged in successfully")
    return {"access_token": access_token, "token_type": "Bearer"}


@router.get("/me", response_model=UserDetailResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.get_user_profile(current_user.email)
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
