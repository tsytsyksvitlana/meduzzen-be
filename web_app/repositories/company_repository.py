from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, subqueryload

from web_app.models import CompanyMembership
from web_app.models.company import Company
from web_app.repositories.base_repository import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, session: AsyncSession):
        super().__init__(Company, session)

    async def get_obj_by_id(self, company_id: int) -> Company:
        query = (
            select(Company)
            .options(
                joinedload(Company.members)
                .joinedload(CompanyMembership.user)
            )
            .where(Company.id == company_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_objs(self, offset: int, limit: int) -> list[Company]:
        query = (
            select(Company)
            .options(
                subqueryload(Company.members)
                .joinedload(CompanyMembership.user)
            )
            .where(Company.is_visible)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def toggle_visibility(self, company: Company):
        company.is_visible = not company.is_visible

    async def update_obj(self, company_id: int, company_data: dict):
        query = (
            update(Company)
            .where(Company.id == company_id)
            .values(**company_data)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(query)
