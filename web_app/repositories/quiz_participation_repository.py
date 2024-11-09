from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from web_app.models.quiz_participation import QuizParticipation
from web_app.repositories.base_repository import BaseRepository


class QuizParticipationRepository(BaseRepository[QuizParticipation]):
    def __init__(self, session: AsyncSession):
        super().__init__(QuizParticipation, session)

    async def get_quizzes_by_user_id(self, user_id: int):
        query = select(QuizParticipation).where(QuizParticipation.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_quizzes_by_user_id_with_quiz(self, user_id: int):
        query = (
            select(QuizParticipation)
            .options(selectinload(QuizParticipation.quiz))
            .where(QuizParticipation.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
