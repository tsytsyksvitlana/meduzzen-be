import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.models import User
from web_app.schemas.user import (
    SignUpRequestModel,
    UserDetailResponse,
    UserSchema,
    UsersListResponse,
    UserUpdateRequestModel
)
from web_app.utils.password_manager import PasswordManager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=UsersListResponse)
async def get_users(
        offset: int = Query(0, ge=0),
        limit: int = Query(10, gt=0),
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> UsersListResponse:
    """
    Fetch all users from the database with optional offset and limit.
    """
    stmt = select(User).offset(offset).limit(limit)
    result = await session.execute(stmt)
    users = result.scalars().all()

    total_count_stmt = select(func.count()).select_from(User)
    total_count_result = await session.execute(total_count_stmt)
    total_count = total_count_result.scalar()

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

    return UsersListResponse(
        users=users_schema,
        total_count=total_count
    )


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
        user_id: int,
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> UserDetailResponse:
    """
    Fetch a user by their ID.
    """
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalars().first()

    if user is None:
        logger.warning(f"User with ID {user_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    logger.info(f"Fetched user with ID {user_id} successfully.")
    _user = UserSchema(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_activity_at=user.last_activity_at
    )
    return UserDetailResponse(user=_user)


@router.post(
    "/", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
        user: SignUpRequestModel,
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> UserDetailResponse:
    """
    Create a new user in the database.
    """
    query = select(User).where(User.email == user.email)
    user_exists = await session.execute(query)
    if user_exists.scalars().first():
        logger.warning(f"User with email {user.email} already exists.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )
    hashed_password = PasswordManager.hash_password(user.password)
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password,
        created_at=datetime.now(),
        last_activity_at=datetime.now(),
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    logger.info(f"Created new user with ID {new_user.id}.")

    user_schema = UserSchema(
        id=new_user.id,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        email=new_user.email,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        last_activity_at=new_user.last_activity_at
    )

    return UserDetailResponse(user=user_schema)


@router.put("/{user_id}", response_model=UserDetailResponse)
async def update_user(
        user_id: int,
        user_update: UserUpdateRequestModel,
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> UserDetailResponse:
    """
    Update an existing user's details.
    """
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalars().first()

    if user is None:
        logger.warning(f"User with ID {user_id} not found for update.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    if user_update.first_name:
        user.first_name = user_update.first_name
    if user_update.last_name:
        user.last_name = user_update.last_name
    await session.commit()
    await session.refresh(user)

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
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> None:
    """
    Delete a user from the database.
    """
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalars().first()

    if user is None:
        logger.warning(f"User with ID {user_id} not found for deletion.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    await session.delete(user)
    await session.commit()

    logger.info(f"Deleted user with ID {user_id}.")
