from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.answer import Answer
from web_app.repositories.base_repository import BaseRepository


class AnswerRepository(BaseRepository[Answer]):
    def __init__(self, session: AsyncSession):
        super().__init__(Answer, session)
