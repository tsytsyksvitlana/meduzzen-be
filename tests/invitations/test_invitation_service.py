import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.exceptions.invitations import (
    InvitationIdAlreadyExistsException,
    InvitationNotFoundException
)
from web_app.exceptions.permission import PermissionDeniedException
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.invitation_repository import InvitationRepository
from web_app.schemas.roles import Role
from web_app.services.invitations.invitation_service import InvitationService

pytestmark = pytest.mark.anyio


@pytest.fixture
async def invitation_service(db_session: AsyncSession):
    membership_repository = CompanyMembershipRepository(session=db_session)
    invitation_repository = InvitationRepository(session=db_session)
    return InvitationService(membership_repository, invitation_repository)


async def test_send_invitation(
    invitation_service: InvitationService,
    db_session: AsyncSession,
    create_test_users,
    create_test_companies
):
    owner = create_test_users[0]
    user = create_test_users[1]
    company = create_test_companies[0]
    await invitation_service.membership_repository.add_user_to_company(
        company_id=company.id, user_id=owner.id, role=Role.OWNER.value
    )
    await invitation_service.membership_repository.session.commit()
    invitation = await invitation_service.send_invitation(
        company.id, owner.id, user.id
    )
    assert invitation.company_id == company.id
    assert invitation.user_id == user.id

    with pytest.raises(InvitationIdAlreadyExistsException):
        await invitation_service.send_invitation(
            company.id, owner.id, user.id
        )


async def test_cancel_invitation(
    invitation_service: InvitationService,
    db_session: AsyncSession,
    create_test_users,
    create_test_companies
):
    owner = create_test_users[0]
    user = create_test_users[1]
    company = create_test_companies[0]
    await invitation_service.membership_repository.add_user_to_company(
        company_id=company.id, user_id=owner.id, role=Role.OWNER.value
    )
    await invitation_service.membership_repository.session.commit()
    invitation = await invitation_service.send_invitation(
        company.id, owner.id, user.id
    )
    await invitation_service.cancel_invitation(invitation.id, owner.id)

    with pytest.raises(InvitationNotFoundException):
        await invitation_service.cancel_invitation(invitation.id + 1, owner.id)


async def test_accept_invitation(
    invitation_service: InvitationService,
    db_session: AsyncSession,
    create_test_users,
    create_test_companies
):
    owner = create_test_users[0]
    user = create_test_users[1]
    company = create_test_companies[0]
    await invitation_service.membership_repository.add_user_to_company(
        company_id=company.id, user_id=owner.id, role=Role.OWNER.value
    )
    await invitation_service.membership_repository.session.commit()
    invitation = await invitation_service.send_invitation(
        company.id, owner.id, user.id
    )
    await invitation_service.accept_invitation(invitation.id, user.id)

    membership = await invitation_service.membership_repository.get_user_company_membership(
        company_id=company.id, user_id=user.id
    )
    assert membership is not None

    with pytest.raises(InvitationNotFoundException):
        await invitation_service.accept_invitation(invitation.id, user.id)


async def test_decline_invitation(
    invitation_service: InvitationService,
    db_session: AsyncSession,
    create_test_users,
    create_test_companies
):
    owner = create_test_users[0]
    user = create_test_users[1]
    company = create_test_companies[0]
    await invitation_service.membership_repository.add_user_to_company(
        company_id=company.id, user_id=owner.id, role=Role.OWNER.value
    )
    await invitation_service.membership_repository.session.commit()
    invitation = await invitation_service.send_invitation(
        company.id, owner.id, user.id
    )
    await invitation_service.decline_invitation(invitation.id, user.id)

    with pytest.raises(InvitationNotFoundException):
        await invitation_service.decline_invitation(invitation.id + 1, user.id)


async def test_get_user_invitations(
    invitation_service: InvitationService,
    db_session: AsyncSession,
    create_test_users,
    create_test_companies
):
    owner = create_test_users[0]
    user = create_test_users[1]
    company = create_test_companies[0]
    await invitation_service.membership_repository.add_user_to_company(
        company_id=company.id, user_id=owner.id, role=Role.OWNER.value
    )
    await invitation_service.membership_repository.session.commit()
    invitation = await invitation_service.send_invitation(
        company.id, owner.id, user.id
    )
    user_invitations, total_count = await invitation_service.get_user_invitations(
        user.id, user.id, limit=10, offset=0
    )
    assert total_count == 1
    assert user_invitations[0].id == invitation.id

    with pytest.raises(PermissionDeniedException):
        await invitation_service.get_user_invitations(
            user.id, create_test_users[0].id, limit=10, offset=0
        )


async def test_get_company_invitations(
    invitation_service: InvitationService,
    db_session: AsyncSession,
    create_test_users,
    create_test_companies
):
    owner = create_test_users[0]
    user = create_test_users[1]
    company = create_test_companies[0]
    await invitation_service.membership_repository.add_user_to_company(
        company_id=company.id, user_id=owner.id, role=Role.OWNER.value
    )
    await invitation_service.membership_repository.session.commit()
    await invitation_service.send_invitation(
        company.id, owner.id, user.id
    )
    invitations, total_count = await invitation_service.get_company_invitations(
        company.id, owner.id, limit=10, offset=0
    )
    assert total_count == 1
    assert invitations[0].user_id == user.id

    with pytest.raises(PermissionDeniedException):
        await invitation_service.get_company_invitations(
            company.id, user.id, limit=10, offset=0
        )
