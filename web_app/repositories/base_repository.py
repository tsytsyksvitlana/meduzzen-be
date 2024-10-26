from typing import Generic

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from web_app.repositories.repository_interface import RepositoryInterface, T


class BaseRepository(RepositoryInterface[T], Generic[T]):
    def __init__(self, model: type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_obj_by_id(self, obj_id: int) -> T | None:
        query = select(self.model).where(self.model.id == obj_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_objs(self, offset: int, limit: int) -> list[T]:
        query = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_obj(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update_obj(self, obj: T, obj_id: int) -> T:
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete_obj(self, obj_id: int) -> T:
        obj = await self.get_obj_by_id(obj_id)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
        return obj

    async def get_obj_count(self) -> int:
        query = select(func.count()).select_from(self.model)
        result = await self.session.execute(query)
        return result.scalar()
