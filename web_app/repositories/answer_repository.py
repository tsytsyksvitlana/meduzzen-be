from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.answer import Answer
from web_app.repositories.base_repository import BaseRepository


class AnswerRepository(BaseRepository[Answer]):
    def __init__(self, session: AsyncSession):
        super().__init__(Answer, session)

    async def get_answers_for_question(self, question_id):
        query = select(Answer).where(Answer.question_id == question_id)
        result = await self.session.execute(query)
        return result.scalars().all()
