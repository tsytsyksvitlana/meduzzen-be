from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.exceptions.auth import AuthorizationException
from web_app.exceptions.users import UserEmailNotFoundException
from web_app.models import User
from web_app.repositories.user_repository import UserRepository
from web_app.schemas.user import SignInRequestModel
from web_app.utils.auth import create_access_token
from web_app.utils.password_manager import PasswordManager


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate_user(self, login_data: SignInRequestModel) -> str:
        db_user = await self.user_repository.get_user_by_email(login_data.email)
        if not db_user:
            raise UserEmailNotFoundException(login_data.email)
        if PasswordManager.verify_password(
                login_data.password, db_user.password
        ):
            return create_access_token(data={"sub": login_data.email})
        raise AuthorizationException(detail="Invalid email or password")

    async def get_user_profile(self, email: str) -> User:
        db_user = await self.user_repository.get_user_by_email(email)
        if not db_user:
            raise UserEmailNotFoundException(email)
        return db_user


def get_auth_service(
    session: AsyncSession = Depends(pg_helper.session_getter)
) -> AuthService:
    return AuthService(user_repository=UserRepository(session))
