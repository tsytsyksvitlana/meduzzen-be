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

    async def get_company_quizzes_by_user_id_with_quiz(self, user_id: int, company_id: int):
        query = (
            select(QuizParticipation)
            .options(selectinload(QuizParticipation.quiz))
            .where((QuizParticipation.user_id == user_id) & (QuizParticipation.company_id == company_id))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_company_participations(self, company_id):
        query = (
            select(QuizParticipation)
            .options(selectinload(QuizParticipation.user))
            .where(QuizParticipation.company_id == company_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_last_participation(self, user_id: int, quiz_id: int):
        result = await self.session.execute(
            select(QuizParticipation)
            .where(QuizParticipation.user_id == user_id, QuizParticipation.quiz_id == quiz_id)
            .order_by(QuizParticipation.participated_at.desc())
        )
        return result.scalars().first()
