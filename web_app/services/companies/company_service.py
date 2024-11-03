from fastapi import Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.models import User
from web_app.models.company import Company
from web_app.models.company_membership import CompanyMembership
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.schemas.company import CompanyCreateSchema


class CompanyService:
    def __init__(
            self,
            company_repository: CompanyRepository,
            membership_repository: CompanyMembershipRepository
    ):
        self.company_repository = company_repository
        self.membership_repository = membership_repository

    async def create_company(self, current_user: User, company_data: CompanyCreateSchema) -> Company:
        try:
            company = Company(**company_data.model_dump())
            company.owner_id = current_user.id
            new_company = await self.company_repository.create_obj(company)

            await self.company_repository.session.commit()
            await self.company_repository.session.refresh(new_company)

            membership = CompanyMembership(company_id=new_company.id, user_id=current_user.id, role="Owner")
            await self.membership_repository.create_obj(membership)

            await self.membership_repository.session.commit()
            return new_company
        except SQLAlchemyError as e:
            await self.company_repository.session.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to create company: {str(e)}")


def get_company_service(
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> CompanyService:
    return CompanyService(
        company_repository=CompanyRepository(session),
        membership_repository=CompanyMembershipRepository(session)
    )
