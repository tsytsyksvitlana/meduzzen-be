from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.user_answer import UserAnswer
from web_app.repositories.base_repository import BaseRepository


class UserAnswerRepository(BaseRepository[UserAnswer]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserAnswer, session)
