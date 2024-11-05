import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.invitation import Invitation
from web_app.repositories.invitation_repository import InvitationRepository

pytestmark = pytest.mark.anyio


async def test_create_invitation(
    db_session: AsyncSession, create_test_companies, create_test_users
):
    invitation_repository = InvitationRepository(session=db_session)
    company = create_test_companies[0]
    user = create_test_users[0]

    invitation_data = Invitation(
        company_id=company.id,
        user_id=user.id,
        status="Pending"
    )

    created_invitation = await invitation_repository.create_obj(invitation_data)
    await invitation_repository.session.commit()

    assert created_invitation.id is not None
    assert created_invitation.company_id == company.id
    assert created_invitation.user_id == user.id
    assert created_invitation.status == "Pending"


async def test_get_invitation(
    db_session: AsyncSession, create_test_companies, create_test_users
):
    invitation_repository = InvitationRepository(session=db_session)
    company = create_test_companies[0]
    user = create_test_users[0]

    invitation_data = Invitation(
        company_id=company.id,
        user_id=user.id,
        status="Pending"
    )
    db_session.add(invitation_data)
    await db_session.commit()

    fetched_invitation = await invitation_repository.get_invitation(
        company.id, user.id
    )

    assert fetched_invitation is not None
    assert fetched_invitation.company_id == company.id
    assert fetched_invitation.user_id == user.id
    assert fetched_invitation.status == "Pending"


async def test_get_user_invitations(
    db_session: AsyncSession, create_test_companies, create_test_users
):
    invitation_repository = InvitationRepository(session=db_session)
    company = create_test_companies[0]
    user = create_test_users[0]

    invitation_data_1 = Invitation(
        company_id=company.id,
        user_id=user.id,
        status="Pending"
    )
    invitation_data_2 = Invitation(
        company_id=company.id,
        user_id=user.id,
        status="Accepted"
    )
    db_session.add_all([invitation_data_1, invitation_data_2])
    await db_session.commit()

    user_invitations = await invitation_repository.get_user_invitations(
        user.id, limit=10, offset=0
    )

    assert len(user_invitations) == 2
    assert user_invitations[0].status == "Pending"
    assert user_invitations[1].status == "Accepted"


async def test_get_invitation_by_id_and_user(
    db_session: AsyncSession, create_test_companies, create_test_users
):
    invitation_repository = InvitationRepository(session=db_session)
    company = create_test_companies[0]
    user = create_test_users[0]

    invitation_data = Invitation(
        company_id=company.id,
        user_id=user.id,
        status="Pending"
    )
    db_session.add(invitation_data)
    await db_session.commit()

    fetched_invitation = await invitation_repository.get_invitation_by_id_and_user(
        invitation_data.id, user.id
    )

    assert fetched_invitation is not None
    assert fetched_invitation.id == invitation_data.id
    assert fetched_invitation.user_id == user.id
    assert fetched_invitation.status == "Pending"


async def test_get_invitations_by_company(
    db_session: AsyncSession, create_test_companies, create_test_users
):
    invitation_repository = InvitationRepository(session=db_session)
    company = create_test_companies[0]
    user = create_test_users[0]

    invitation_data_1 = Invitation(
        company_id=company.id,
        user_id=user.id,
        status="Pending"
    )
    invitation_data_2 = Invitation(
        company_id=company.id,
        user_id=user.id,
        status="Accepted"
    )
    db_session.add_all([invitation_data_1, invitation_data_2])
    await db_session.commit()

    company_invitations = await invitation_repository.get_invitations_by_company(
        company.id, limit=10, offset=0
    )

    assert len(company_invitations) == 2
    assert company_invitations[0].status == "Pending"
    assert company_invitations[1].status == "Accepted"


async def test_get_total_invitations_count(
    db_session: AsyncSession, create_test_companies, create_test_users
):
    invitation_repository = InvitationRepository(session=db_session)
    company = create_test_companies[0]
    user = create_test_users[0]

    invitation_data_1 = Invitation(
        company_id=company.id,
        user_id=user.id,
        status="Pending"
    )
    invitation_data_2 = Invitation(
        company_id=company.id,
        user_id=user.id,
        status="Accepted"
    )
    db_session.add_all([invitation_data_1, invitation_data_2])
    await db_session.commit()

    total_invitations_count = await invitation_repository.get_total_invitations_count(
        user.id
    )

    assert total_invitations_count == 2


async def test_get_total_invitations_count_by_company(
    db_session: AsyncSession, create_test_companies, create_test_users
):
    invitation_repository = InvitationRepository(session=db_session)
    company = create_test_companies[0]
    user = create_test_users[0]

    invitation_data_1 = Invitation(
        company_id=company.id,
        user_id=user.id,
        status="Pending"
    )
    invitation_data_2 = Invitation(
        company_id=company.id,
        user_id=user.id,
        status="Accepted"
    )
    db_session.add_all([invitation_data_1, invitation_data_2])
    await db_session.commit()

    total_invitations_count = await invitation_repository.get_total_invitations_count_by_company(
        company.id
    )

    assert total_invitations_count == 2


async def test_update_invitation_status(
    db_session: AsyncSession, create_test_companies, create_test_users
):
    invitation_repository = InvitationRepository(session=db_session)
    company = create_test_companies[0]
    user = create_test_users[0]

    invitation_data = Invitation(
        company_id=company.id,
        user_id=user.id,
        status="Pending"
    )
    db_session.add(invitation_data)
    await db_session.commit()

    invitation_data.status = "Accepted"
    updated_invitation = await invitation_repository.update_obj(invitation_data)
    await db_session.commit()

    assert updated_invitation is not None
    assert updated_invitation.status == "Accepted"

    fetched_invitation = await invitation_repository.get_invitation_by_id_and_user(
        invitation_data.id, user.id
    )
    assert fetched_invitation.status == "Accepted"


async def test_delete_invitation(
    db_session: AsyncSession, create_test_companies, create_test_users
):
    invitation_repository = InvitationRepository(session=db_session)
    company = create_test_companies[0]
    user = create_test_users[0]

    invitation_data = Invitation(
        company_id=company.id,
        user_id=user.id,
        status="Pending"
    )
    db_session.add(invitation_data)
    await db_session.commit()

    deleted_invitation = await invitation_repository.delete_obj(invitation_data.id)
    await invitation_repository.session.commit()

    assert deleted_invitation.id == invitation_data.id
    assert await invitation_repository.get_invitation_by_id_and_user(
        invitation_data.id, user.id
    ) is None
