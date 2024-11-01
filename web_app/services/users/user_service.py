from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.exceptions.users import (
    UserEmailNotFoundException,
    UserIdAlreadyExistsException,
    UserIdNotFoundException
)
from web_app.models import User
from web_app.repositories.user_repository import UserRepository
from web_app.schemas.user import SignUpRequestModel, UserUpdateRequestModel
from web_app.utils.password_manager import PasswordManager


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.user_repository.get_obj_by_id(user_id)
        if not user:
            raise UserIdNotFoundException(user_id)
        return user

    async def get_users(self, offset: int, limit: int):
        users = await self.user_repository.get_objs(offset, limit)
        total_count = await self.user_repository.get_obj_count()
        return users, total_count

    async def create_user(self, user_data: SignUpRequestModel) -> User:
        existing_user = await self.user_repository.get_user_by_email(
            user_data.email
        )
        if existing_user:
            raise UserIdAlreadyExistsException(user_data.email)

        hashed_password = PasswordManager.hash_password(user_data.password)
        new_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            password=hashed_password
        )
        return await self.user_repository.create_obj(new_user)

    async def update_user(
            self, user_id: int, user_update: UserUpdateRequestModel
    ) -> User:
        user = await self.get_user_by_id(user_id)
        if user_update.first_name:
            user.first_name = user_update.first_name
        if user_update.last_name:
            user.last_name = user_update.last_name
        return await self.user_repository.update_obj(user, user_id)

    async def delete_user(self, user_id: int):
        user = await self.get_user_by_id(user_id)
        await self.user_repository.delete_obj(user.id)

    async def get_user_by_email(self, email: str) -> User:
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise UserEmailNotFoundException(email)
        return user

    async def create_user_by_email(self, email: str) -> User:
        existing_user = await self.user_repository.get_user_by_email(email)
        if existing_user:
            return existing_user

        new_user = User(
            first_name=email.split('@')[0],
            last_name="",
            email=email,
            password=PasswordManager.return_default_password()
        )
        return await self.user_repository.create_obj(new_user)


def get_user_service(
    session: AsyncSession = Depends(pg_helper.session_getter)
) -> UserService:
    return UserService(user_repository=UserRepository(session))
