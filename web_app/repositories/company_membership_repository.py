from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models import User
from web_app.models.company_membership import CompanyMembership
from web_app.repositories.base_repository import BaseRepository
from web_app.schemas.roles import Role


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

    async def add_user_to_company(
            self, company_id: int, user_id: int, role: str = Role.MEMBER.value
    ):
        new_membership = CompanyMembership(
            company_id=company_id,
            user_id=user_id,
            role=role
        )
        self.session.add(new_membership)

    async def get_users_by_ids(self, user_ids: list[int], limit: int, offset: int) -> list[User]:
        query = (
            select(User)
            .where(User.id.in_(user_ids))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
