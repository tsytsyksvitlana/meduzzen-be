from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.company_membership import CompanyMembership
from web_app.repositories.base_repository import BaseRepository


class CompanyMembershipRepository(BaseRepository[CompanyMembership]):
    def __init__(self, session: AsyncSession):
        super().__init__(CompanyMembership, session)

    async def get_user_company_membership(
        self, company_id: int, user_id: int
    ) -> CompanyMembership | None:
        query = (
            select(CompanyMembership)
            .where(
                CompanyMembership.company_id == company_id,
                CompanyMembership.user_id == user_id
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_memberships_by_company_id(self, company_id: int):
        query = select(CompanyMembership).filter_by(company_id=company_id)
        result = await self.session.execute(query)
        return result.scalars().all()
