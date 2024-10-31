from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models import User
from web_app.repositories.base_repository import BaseRepository
from web_app.utils.password_manager import PasswordManager


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_user_by_email(self, email: EmailStr) -> User | None:
        query = select(self.model).where(self.model.email == email)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update_user_password(self, current_user, new_password):
        hashed_password = PasswordManager.hash_password(new_password)
        current_user.password = hashed_password
        self.session.add(current_user)
        await self.session.commit()

    async def set_user_password(self, current_user, password):
        hashed_password = PasswordManager.hash_password(password)
        current_user.password = hashed_password
        self.session.add(current_user)
        await self.session.commit()
