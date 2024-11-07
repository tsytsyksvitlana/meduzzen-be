from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.question import Question
from web_app.repositories.base_repository import BaseRepository


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, session: AsyncSession):
        super().__init__(Question, session)

    async def get_questions_for_quiz(self, quiz_id: int):
        query = select(Question).filter(Question.quiz_id == quiz_id)
        result = await self.session.execute(query)
        return result.scalars().all()
