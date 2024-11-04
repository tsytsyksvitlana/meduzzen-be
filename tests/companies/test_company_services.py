import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.exceptions.companies import CompanyNotFoundException
from web_app.exceptions.permission import PermissionDeniedException
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.schemas.company import CompanyCreateSchema, CompanyUpdateSchema
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
    fetched_company = await company_service.get_company(company_from_fixture.id)

    assert fetched_company.name == company_from_fixture.name

    with pytest.raises(CompanyNotFoundException):
        await company_service.get_company(-1)


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

    toggled_company = await company_service.get_company(company_to_toggle.id)

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
