import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.exceptions.companies import CompanyNotFoundException
from web_app.exceptions.memberships import MembershipException
from web_app.exceptions.permission import PermissionDeniedException
from web_app.models import Company, CompanyMembership, User
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.schemas.company import CompanyCreateSchema, CompanyUpdateSchema
from web_app.schemas.roles import Role
from web_app.services.companies.company_service import CompanyService

pytestmark = pytest.mark.anyio


@pytest.fixture
async def create_test_companies(db_session: AsyncSession, create_test_users):
    user = create_test_users[0]
    company_repository = CompanyRepository(session=db_session)
    membership_repository = CompanyMembershipRepository(session=db_session)
    company_service = CompanyService(company_repository, membership_repository)

    company_data = CompanyCreateSchema(
        name="New Tech Company",
        description="A company dedicated to technology.",
        is_visible=True,
        address="100 Test St.",
        contact_email="contact@testcompany1.com",
        phone_number="1112223333"
    )

    created_company = await company_service.create_company(user, company_data)
    return [created_company]


async def test_company_service_create_company(
    db_session: AsyncSession,
    create_test_users
):
    user = create_test_users[0]
    company_repository = CompanyRepository(session=db_session)
    membership_repository = CompanyMembershipRepository(session=db_session)
    company_service = CompanyService(company_repository, membership_repository)

    company_data = CompanyCreateSchema(
        name="New Tech Company",
        description="A company dedicated to technology.",
        is_visible=True,
        address="100 Test St.",
        contact_email="contact@testcompany1.com",
        phone_number="1112223333"
    )

    created_company = await company_service.create_company(user, company_data)

    assert created_company.name == company_data.name


async def test_company_service_get_company(
    db_session: AsyncSession,
    create_test_companies
):
    company_repository = CompanyRepository(session=db_session)
    membership_repository = CompanyMembershipRepository(session=db_session)
    company_service = CompanyService(company_repository, membership_repository)

    company_from_fixture = create_test_companies[0]
    fetched_company = await company_service.get_company_with_members(
        company_from_fixture.id)

    assert fetched_company.name == company_from_fixture.name

    with pytest.raises(CompanyNotFoundException):
        await company_service.get_company_with_members(-1)


async def test_company_service_update_company(
    db_session: AsyncSession,
    create_test_companies,
    create_test_users
):
    user = create_test_users[0]
    company_repository = CompanyRepository(session=db_session)
    membership_repository = CompanyMembershipRepository(session=db_session)
    company_service = CompanyService(company_repository, membership_repository)

    company_to_update = create_test_companies[0]
    company_update_data = CompanyUpdateSchema(name="Updated Tech Corp")

    updated_company = await company_service.update_company(
        company_to_update.id,
        company_update_data,
        current_user=user
    )

    assert updated_company.name == "Updated Tech Corp"

    non_owner_user = create_test_users[1]
    with pytest.raises(PermissionDeniedException):
        await company_service.update_company(
            company_to_update.id,
            company_update_data,
            current_user=non_owner_user
        )


async def test_company_service_toggle_visibility(
    db_session: AsyncSession,
    create_test_companies,
    create_test_users
):
    user = create_test_users[0]
    company_repository = CompanyRepository(session=db_session)
    membership_repository = CompanyMembershipRepository(session=db_session)
    company_service = CompanyService(company_repository, membership_repository)

    company_to_toggle = create_test_companies[0]

    assert company_to_toggle.is_visible is True

    await company_service.toggle_visibility(company_to_toggle.id, user)

    toggled_company = await company_service.get_company_with_members(
        company_to_toggle.id)

    assert toggled_company.is_visible is False

    non_owner_user = create_test_users[1]
    with pytest.raises(PermissionDeniedException):
        await company_service.toggle_visibility(
            company_to_toggle.id, current_user=non_owner_user
        )


async def test_company_service_delete_company(
    db_session: AsyncSession,
    create_test_companies,
    create_test_users
):
    user = create_test_users[0]
    company_repository = CompanyRepository(session=db_session)
    membership_repository = CompanyMembershipRepository(session=db_session)
    company_service = CompanyService(company_repository, membership_repository)

    company_to_delete = create_test_companies[0]
    await company_service.delete_company(company_to_delete.id, current_user=user)

    non_owner_user = create_test_users[1]
    with pytest.raises(PermissionDeniedException):
        await company_service.delete_company(
            company_to_delete.id, current_user=non_owner_user
        )


async def test_appoint_admin(
    db_session: AsyncSession,
    create_test_companies,
    create_test_users
):
    user = create_test_users[0]
    other_user = create_test_users[1]
    company_repository = CompanyRepository(session=db_session)
    membership_repository = CompanyMembershipRepository(session=db_session)
    company_service = CompanyService(company_repository, membership_repository)

    company_to_update = create_test_companies[0]

    await membership_repository.add_user_to_company(company_to_update.id, other_user.id)
    await db_session.commit()

    membership = await company_service.appoint_admin(
        company_to_update.id, other_user.id, current_user=user
    )

    assert membership.role == Role.ADMIN.value

    with pytest.raises(MembershipException):
        await company_service.appoint_admin(
            company_to_update.id, other_user.id, current_user=user
        )

    with pytest.raises(MembershipException):
        await company_service.appoint_admin(
            company_to_update.id, other_user.id + 1, current_user=user
        )


async def test_remove_admin(
        db_session: AsyncSession,
        create_test_companies,
        create_test_users
):
    user = create_test_users[0]
    other_user = create_test_users[1]
    company_repository = CompanyRepository(session=db_session)
    membership_repository = CompanyMembershipRepository(session=db_session)
    company_service = CompanyService(company_repository, membership_repository)

    company_to_update = create_test_companies[0]

    await membership_repository.add_user_to_company(company_to_update.id, other_user.id)
    await membership_repository.session.commit()

    await company_service.appoint_admin(
        company_to_update.id, other_user.id, current_user=user
    )

    membership = await membership_repository.get_user_company_membership(
        company_to_update.id, other_user.id
    )
    assert membership.role == Role.ADMIN.value

    updated_membership = await company_service.remove_admin(
        company_to_update.id, other_user.id, current_user=user
    )

    assert updated_membership.role == Role.MEMBER.value

    with pytest.raises(MembershipException):
        await company_service.remove_admin(
            company_to_update.id, user.id, current_user=user
        )


async def test_get_admins_in_company_success(db_session: AsyncSession):
    company_repository = CompanyRepository(db_session)
    membership_repository = CompanyMembershipRepository(db_session)

    company = Company(name="Test Company", description="Description", is_visible=True)
    await company_repository.create_obj(company)
    await company_repository.session.commit()

    admin1 = User(first_name="admin1", email="admin1@example.com")
    admin2 = User(first_name="admin2", email="admin2@example.com")
    member = User(first_name="member1", email="member1@example.com")

    company_repository.session.add(admin1)
    company_repository.session.add(admin2)
    company_repository.session.add(member)
    await company_repository.session.commit()

    await membership_repository.create_obj(
        CompanyMembership(company_id=company.id, user_id=admin1.id, role=Role.ADMIN.value))
    await membership_repository.create_obj(
        CompanyMembership(company_id=company.id, user_id=admin2.id, role=Role.ADMIN.value))
    await membership_repository.create_obj(
        CompanyMembership(company_id=company.id, user_id=member.id, role=Role.MEMBER.value))
    await membership_repository.session.commit()

    company_service = CompanyService(
        company_repository=company_repository,
        membership_repository=membership_repository
    )

    limit = 10
    offset = 0
    users, total_count = await company_service.get_admins_in_company(company.id, limit, offset)

    assert total_count == 2
    assert len(users) == 2
    assert users[0].first_name == "admin1"
    assert users[1].first_name == "admin2"


async def test_get_admins_in_company_company_not_found(db_session: AsyncSession,):
    company_repository = CompanyRepository(db_session)
    membership_repository = CompanyMembershipRepository(db_session)
    company_service = CompanyService(
        company_repository=company_repository,
        membership_repository=membership_repository
    )

    with pytest.raises(CompanyNotFoundException):
        await company_service.get_admins_in_company(999, 10, 0)
