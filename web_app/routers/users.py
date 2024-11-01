import logging

from fastapi import APIRouter, Depends, Query, status

from web_app.schemas.user import (
    UserDetailResponse,
    UserSchema,
    UsersListResponse,
    UserUpdateRequestModel
)
from web_app.services.users.user_service import UserService
from web_app.utils.auth import get_user_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=UsersListResponse)
async def get_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    user_service: UserService = Depends(get_user_service)
) -> UsersListResponse:
    """
    Fetch all users from the database with optional offset and limit.
    """
    users, total_count = await user_service.get_users(offset, limit)
    logger.info("Fetched users successfully.")
    users_schema = [
        UserSchema(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_activity_at=user.last_activity_at
        )
        for user in users
    ]
    return UsersListResponse(users=users_schema, total_count=total_count)


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
) -> UserDetailResponse:
    """
    Fetch a user by their ID.
    """
    user = await user_service.get_user_by_id(user_id)
    logger.info(f"Fetched user with ID {user_id} successfully.")
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


@router.put("/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdateRequestModel,
    user_service: UserService = Depends(get_user_service)
) -> UserDetailResponse:
    """
    Update an existing user's details.
    """
    user = await user_service.update_user(user_id, user_update)
    logger.info(f"Updated user with ID {user_id}.")
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


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
) -> None:
    """
    Delete a user from the database.
    """
    await user_service.delete_user(user_id)
    logger.info(f"Deleted user with ID {user_id}.")
