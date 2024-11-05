from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.exceptions.invitations import (
    InvitationIdAlreadyExistsException,
    InvitationNotFoundException
)
from web_app.exceptions.permission import PermissionDeniedException
from web_app.models import Invitation
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.invitation_repository import InvitationRepository
from web_app.schemas.invitation import InvitationStatus
from web_app.schemas.roles import Role


class InvitationService:
    def __init__(
        self,
        membership_repository: CompanyMembershipRepository,
        invitation_repository: InvitationRepository,
    ):
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

    async def get_user_invitations(
        self,
        user_id: int,
        current_user_id: int,
        limit: int,
        offset: int
    ) -> tuple[list[Invitation], int]:
        if current_user_id != user_id:
            raise PermissionDeniedException()
        invitations = await self.invitation_repository.get_user_invitations(
            current_user_id, limit, offset
        )
        total_count = await self.invitation_repository.get_total_invitations_count(
            current_user_id
        )
        return invitations, total_count

    async def accept_invitation(self, invitation_id: int, user_id: int):
        invitation = await self.invitation_repository.get_invitation_by_id_and_user(
            invitation_id, user_id
        )
        if not invitation or invitation.status != InvitationStatus.PENDING.value:
            raise InvitationNotFoundException(invitation_id)

        invitation.status = InvitationStatus.ACCEPTED.value
        await self.membership_repository.add_user_to_company(invitation.company_id, user_id)
        await self.invitation_repository.update_obj(invitation)
        await self.invitation_repository.session.commit()

    async def decline_invitation(self, invitation_id: int, user_id: int):
        invitation = await self.invitation_repository.get_invitation_by_id_and_user(
            invitation_id, user_id
        )
        if not invitation:
            raise InvitationNotFoundException(invitation_id)

        invitation.status = InvitationStatus.CANCELED.value
        await self.invitation_repository.update_obj(invitation)
        await self.invitation_repository.session.commit()

    async def cancel_invitation(self, invitation_id: int, owner_id: int):
        invitation = await self.invitation_repository.get_obj_by_id(invitation_id)
        owner_membership = await self.membership_repository.get_user_company_membership(
            invitation.company_id, owner_id
        )
        if not invitation or not owner_membership or owner_membership.role != Role.OWNER.value:
            raise PermissionDeniedException()

        invitation.status = InvitationStatus.CANCELED.value
        await self.invitation_repository.update_obj(invitation)
        await self.invitation_repository.session.commit()

    async def get_company_invitations(
            self,
            company_id: int,
            owner_id: int,
            limit: int,
            offset: int
    ) -> tuple[list[Invitation], int]:
        owner_membership = await self.membership_repository.get_user_company_membership(
            company_id, owner_id
        )
        if not owner_membership or owner_membership.role != Role.OWNER.value:
            raise PermissionDeniedException()

        invitations = await self.invitation_repository.get_invitations_by_company(company_id, limit, offset)
        total_count = await self.invitation_repository.get_total_invitations_count_by_company(company_id)

        return invitations, total_count


def get_invitation_service(
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> InvitationService:
    return InvitationService(
        membership_repository=CompanyMembershipRepository(session),
        invitation_repository=InvitationRepository(session),
    )
