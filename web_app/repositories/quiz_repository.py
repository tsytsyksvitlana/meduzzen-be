from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.quiz import Quiz
from web_app.repositories.base_repository import BaseRepository


class QuizRepository(BaseRepository[Quiz]):
    def __init__(self, session: AsyncSession):
        super().__init__(Quiz, session)

    async def get_objs(self, company_id: int, skip: int, limit: int):
        query = select(Quiz).filter(Quiz.company_id == company_id).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all_objs(self):
        query = select(Quiz)
        result = await self.session.execute(query)
        return result.scalars().all()
