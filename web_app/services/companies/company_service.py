from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.exceptions.application import ApplicationErrorException
from web_app.exceptions.companies import (
    CompanyNotFoundException,
    OwnerNotFoundException
)
from web_app.exceptions.permission import PermissionDeniedException
from web_app.models import User
from web_app.models.company import Company
from web_app.models.company_membership import CompanyMembership
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.schemas.company import CompanyCreateSchema, CompanyUpdateSchema
from web_app.schemas.roles import Role


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
        if not membership or membership.role != Role.OWNER:
            raise PermissionDeniedException()

    async def get_company_with_members(self, company_id: int):
        company = await self.company_repository.get_obj_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id)

        members = await self.membership_repository.get_memberships_by_company_id(company_id)
        company.members = members

        owners = list(filter(lambda membership: membership.role == Role.OWNER, members))
        if not owners:
            raise OwnerNotFoundException(company_id)
        company.owner = owners[0].user
        return company

    async def get_companies_with_owners(
            self, limit: int, offset: int
    ) -> tuple[list[Company], int]:
        companies = await self.company_repository.get_objs(offset=offset, limit=limit)
        total_count = await self.company_repository.get_obj_count()

        for company in companies:
            owners = [
                membership.user for membership in company.members
                if membership.role == Role.OWNER
            ]
            company.owner = owners[0] if owners else None

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
                company_id=new_company.id, user_id=current_user.id, role=Role.OWNER
            )
            await self.membership_repository.create_obj(membership)

            await self.membership_repository.session.commit()
            return new_company
        except SQLAlchemyError:
            await self.company_repository.session.rollback()
            raise ApplicationErrorException(
                "An error occurred while creating company."
            )

    async def toggle_visibility(self, company_id: int, current_user: User) -> Company:
        await self.check_is_owner(company_id, current_user)

        company = await self.get_company_with_members(company_id)

        await self.company_repository.toggle_visibility(company)
        await self.company_repository.session.commit()
        await self.company_repository.session.refresh(company)

        return company

    async def delete_company(self, company_id: int, current_user: User):
        await self.check_is_owner(company_id, current_user)

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

        updated_fields = {
            "name": company_data.name or company.name,
            "description": company_data.description or company.description,
            "address": company_data.address or company.address,
        }

        await self.company_repository.update_obj(company_id, updated_fields)
        await self.company_repository.session.commit()
        await self.company_repository.session.refresh(company)

        updated_company = await self.company_repository.get_obj_by_id(company_id)

        return updated_company


def get_company_service(
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> CompanyService:
    return CompanyService(
        company_repository=CompanyRepository(session),
        membership_repository=CompanyMembershipRepository(session)
    )
