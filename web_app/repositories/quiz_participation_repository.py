from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.quiz_participation import QuizParticipation
from web_app.repositories.base_repository import BaseRepository


class QuizParticipationRepository(BaseRepository[QuizParticipation]):
    def __init__(self, session: AsyncSession):
        super().__init__(QuizParticipation, session)
