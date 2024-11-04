from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.exceptions.invitations import InvitationIdAlreadyExistsException
from web_app.exceptions.permission import PermissionDeniedException
from web_app.models import Invitation
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.repositories.invitation_repository import InvitationRepository
from web_app.schemas.roles import Role


class InvitationService:
    def __init__(
        self,
        company_repository: CompanyRepository,
        membership_repository: CompanyMembershipRepository,
        invitation_repository: InvitationRepository,
    ):
        self.company_repository = company_repository
        self.membership_repository = membership_repository
        self.invitation_repository = invitation_repository

    async def send_invitation(
            self,
            company_id: int,
            owner_id: int,
            user_id: int
    ) -> Invitation:
        owner_membership = await self.membership_repository.get_user_company_membership(
            company_id, owner_id
        )
        if not owner_membership or owner_membership.role != Role.OWNER.value:
            raise PermissionDeniedException()

        existing_invitation = await self.invitation_repository.get_invitation(
            company_id, user_id
        )

        if existing_invitation:
            raise InvitationIdAlreadyExistsException(existing_invitation.id)

        invitation = Invitation(
            company_id=company_id,
            user_id=user_id,
            status="Pending",
        )
        invitation = await self.invitation_repository.create_obj(invitation)
        await self.invitation_repository.session.commit()
        return invitation

    async def get_user_invitations(self, user_id: int, limit: int, offset: int) -> tuple[list[Invitation], int]:
        invitations = await self.invitation_repository.get_user_invitations(user_id, limit, offset)
        total_count = await self.invitation_repository.get_total_invitations_count(user_id)
        return invitations, total_count


def get_invitation_service(
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> InvitationService:
    return InvitationService(
        company_repository=CompanyRepository(session),
        membership_repository=CompanyMembershipRepository(session),
        invitation_repository=InvitationRepository(session),
    )
