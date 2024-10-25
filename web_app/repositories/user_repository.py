from pydantic import EmailStr
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.exceptions.users import UserNotFoundException
from web_app.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int) -> User:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user is None:
            raise UserNotFoundException(user_id)
        return user

    async def get_users(self, offset: int, limit: int):
        stmt = select(User).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return users

    async def count_users(self):
        total_count_stmt = select(func.count()).select_from(User)
        total_count_result = await self.session.execute(total_count_stmt)
        return total_count_result.scalar()

    async def create_user(self, user_data: User) -> User:
        self.session.add(user_data)
        await self.session.commit()
        await self.session.refresh(user_data)
        return user_data

    async def update_user(self, user: User) -> User:
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user: User):
        await self.session.delete(user)
        await self.session.commit()

    async def get_user_by_email(self, email: EmailStr) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalars().first()
