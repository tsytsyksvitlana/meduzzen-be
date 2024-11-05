from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.exceptions.companies import CompanyNotFoundException
from web_app.exceptions.join_requests import (
    JoinRequestAlreadyExistsException,
    JoinRequestNotFoundException
)
from web_app.exceptions.permission import PermissionDeniedException
from web_app.models import JoinRequest
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.repositories.join_request_repository import JoinRequestRepository
from web_app.schemas.roles import Role


class JoinRequestService:
    def __init__(
        self,
        join_request_repository: JoinRequestRepository,
        membership_repository: CompanyMembershipRepository,
        company_repository: CompanyRepository,
    ):
        self.join_request_repository = join_request_repository
        self.membership_repository = membership_repository
        self.company_repository = company_repository

    async def request_to_join(self, company_id: int, user_id: int) -> JoinRequest:
        existing_request = await self.join_request_repository.get_request(
            company_id, user_id
        )
        if existing_request:
            raise JoinRequestAlreadyExistsException(existing_request.id)
        company = await self.company_repository.get_obj_by_id(company_id)
        if company is None:
            raise CompanyNotFoundException(company_id)

        join_request = JoinRequest(company_id=company_id, user_id=user_id)
        join_request = await self.join_request_repository.create_obj(join_request)
        await self.join_request_repository.session.commit()
        return join_request

    async def cancel_request(self, request_id: int, user_id: int):
        join_request = await self.join_request_repository.get_obj_by_id(request_id)
        if not join_request or join_request.user_id != user_id:
            raise JoinRequestNotFoundException(request_id)

        await self.join_request_repository.delete_obj(join_request.id)
        await self.join_request_repository.session.commit()

    async def accept_request(self, request_id: int, owner_id: int):
        join_request = await self.join_request_repository.get_obj_by_id(request_id)
        if not join_request:
            raise JoinRequestNotFoundException(request_id)

        await self.membership_repository.add_user_to_company(
            join_request.company_id, join_request.user_id
        )
        await self.join_request_repository.delete_obj(join_request.id)
        await self.join_request_repository.session.commit()

    async def decline_request(self, request_id: int, owner_id: int):
        join_request = await self.join_request_repository.get_obj_by_id(request_id)
        if not join_request:
            raise JoinRequestNotFoundException(request_id)

        await self.join_request_repository.delete_obj(join_request.id)
        await self.join_request_repository.session.commit()

    async def get_user_requests(self, user_id: int, current_user_id) -> list[JoinRequest]:
        if current_user_id != user_id:
            raise PermissionDeniedException()
        return await self.join_request_repository.get_user_requests(user_id)

    async def check_is_owner(self, company_id: int, user_id: int):
        membership = await self.membership_repository.get_user_company_membership(
            company_id=company_id, user_id=user_id
        )
        if not membership or membership.role != Role.OWNER.value:
            raise PermissionDeniedException()

    async def get_pending_requests(self, company_id: int, current_user_id: int) -> list[JoinRequest]:
        await self.check_is_owner(company_id, current_user_id)
        return await self.join_request_repository.get_pending_requests(company_id)


def get_join_request_service(
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> JoinRequestService:
    return JoinRequestService(
        membership_repository=CompanyMembershipRepository(session),
        join_request_repository=JoinRequestRepository(session),
        company_repository=CompanyRepository(session),
    )
