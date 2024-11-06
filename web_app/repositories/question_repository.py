from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.question import Question
from web_app.repositories.base_repository import BaseRepository


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, session: AsyncSession):
        super().__init__(Question, session)
