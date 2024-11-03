from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.company_membership import CompanyMembership
from web_app.repositories.base_repository import BaseRepository


class CompanyMembershipRepository(BaseRepository[CompanyMembership]):
    def __init__(self, session: AsyncSession):
        super().__init__(CompanyMembership, session)
