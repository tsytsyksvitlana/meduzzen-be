from fastapi import Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.exceptions.companies import CompanyNotFoundException
from web_app.exceptions.permission import PermissionDeniedException
from web_app.models import User
from web_app.models.company import Company
from web_app.models.company_membership import CompanyMembership
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.schemas.company import CompanyCreateSchema, CompanyUpdateSchema


class CompanyService:
    def __init__(
        self,
        company_repository: CompanyRepository,
        membership_repository: CompanyMembershipRepository
    ):
        self.company_repository = company_repository
        self.membership_repository = membership_repository

    async def check_is_owner(self, company_id: int, user: User):
        membership = await self.membership_repository.get_user_company_membership(
            company_id=company_id, user_id=user.id
        )
        if not membership or membership.role != "Owner":
            raise PermissionDeniedException()

    async def get_company(self, company_id: int):
        company = await self.company_repository.get_obj_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id)
        return company

    async def get_companies(
        self, limit: int, offset: int
    ) -> tuple[list[Company], int]:
        companies = await self.company_repository.get_objs(offset=offset, limit=limit)
        total_count = await self.company_repository.get_obj_count()
        return companies, total_count

    async def create_company(
        self, current_user: User, company_data: CompanyCreateSchema
    ) -> Company:
        try:
            company = Company(**company_data.model_dump())
            company.owner_id = current_user.id
            new_company = await self.company_repository.create_obj(company)

            await self.company_repository.session.commit()
            await self.company_repository.session.refresh(new_company)

            membership = CompanyMembership(
                company_id=new_company.id, user_id=current_user.id, role="Owner"
            )
            await self.membership_repository.create_obj(membership)

            await self.membership_repository.session.commit()
            return new_company
        except SQLAlchemyError as e:
            await self.company_repository.session.rollback()
            raise HTTPException(
                status_code=400, detail=f"Failed to create company: {str(e)}"
            )

    async def toggle_visibility(self, company_id: int, current_user: User) -> Company:
        await self.check_is_owner(company_id, current_user)

        company = await self.company_repository.get_obj_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id)

        company.is_visible = not company.is_visible
        await self.company_repository.toggle_visibility(company)
        await self.company_repository.session.commit()
        await self.company_repository.session.refresh(company)
        return company

    async def delete_company(self, company_id: int, current_user: User):
        await self.check_is_owner(company_id, current_user)

        company = await self.company_repository.get_obj_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id)
        await self.company_repository.delete_obj(company_id)
        await self.company_repository.session.commit()

    async def update_company(
            self,
            company_id: int,
            company_data: CompanyUpdateSchema,
            current_user: User
    ):
        await self.check_is_owner(company_id, current_user)

        company = await self.company_repository.get_obj_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id)

        updated_fields = {
            "name": company_data.name if company_data.name is not None else company.name,
            "description": company_data.description if company_data.description is not None else company.description,
            "address": company_data.address if company_data.address is not None else company.address,
        }

        await self.company_repository.update_obj(company_id, updated_fields)
        await self.company_repository.session.commit()

        updated_company = await self.company_repository.get_obj_by_id(company_id)

        return updated_company


def get_company_service(
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> CompanyService:
    return CompanyService(
        company_repository=CompanyRepository(session),
        membership_repository=CompanyMembershipRepository(session)
    )
