from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.company import Company
from web_app.repositories.base_repository import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, session: AsyncSession):
        super().__init__(Company, session)
