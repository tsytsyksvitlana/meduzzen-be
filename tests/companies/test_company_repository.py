import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models import Company, CompanyMembership
from web_app.repositories.company_repository import CompanyRepository
from web_app.schemas.roles import Role

pytestmark = pytest.mark.anyio


async def test_create_company(db_session: AsyncSession):
    company_repository = CompanyRepository(session=db_session)
    company_data = Company(
        name="Tech Corp",
        description="A tech company.",
        is_visible=True,
        address="123 Tech Lane",
        contact_email="info@techcorp.com",
        phone_number="123-456-7890"
    )

    created_company = await company_repository.create_obj(company_data)
    await company_repository.session.commit()

    assert created_company.id is not None
    assert created_company.name == company_data.name


async def test_get_company_by_id(
    db_session: AsyncSession, create_test_companies
):
    company_repository = CompanyRepository(session=db_session)
    company_data = create_test_companies[0]

    fetched_company = await company_repository.get_obj_by_id(company_data.id)

    assert fetched_company is not None
    assert fetched_company.id == company_data.id
    assert fetched_company.name == company_data.name


async def test_update_company(
    db_session: AsyncSession, create_test_companies
):
    company_repository = CompanyRepository(session=db_session)
    company_data = create_test_companies[0]

    new_name = "Updated Tech Corp"
    await company_repository.update_obj(company_data.id, {"name": new_name})
    await company_repository.session.commit()

    updated_company = await company_repository.get_obj_by_id(company_data.id)

    assert updated_company is not None
    assert updated_company.name == new_name


async def test_delete_company(
    db_session: AsyncSession, create_test_companies
):
    company_repository = CompanyRepository(session=db_session)
    company_data = create_test_companies[0]

    deleted_company = await company_repository.delete_obj(company_data.id)
    await company_repository.session.commit()

    assert deleted_company.id == company_data.id
    assert await company_repository.get_obj_by_id(company_data.id) is None


async def test_toggle_company_visibility(
        db_session: AsyncSession, create_test_companies
):
    company_repository = CompanyRepository(session=db_session)
    company_data = create_test_companies[0]

    await company_repository.toggle_visibility(company_data)
    await company_repository.session.commit()

    await db_session.refresh(company_data)
    assert company_data.is_visible is False

    await company_repository.toggle_visibility(company_data)
    await company_repository.session.commit()

    await db_session.refresh(company_data)
    assert company_data.is_visible is True


async def test_get_users_for_company(
        db_session: AsyncSession, create_test_companies, create_test_users
):
    company_repository = CompanyRepository(session=db_session)
    company_data = create_test_companies[0]
    user_member = create_test_users[0]
    user_owner = create_test_users[1]

    member_membership = CompanyMembership(
        company_id=company_data.id,
        user_id=user_member.id,
        role=Role.MEMBER.value,
    )
    owner_membership = CompanyMembership(
        company_id=company_data.id,
        user_id=user_owner.id,
        role=Role.OWNER.value,
    )
    db_session.add_all([member_membership, owner_membership])
    await db_session.commit()

    company_members = await company_repository.get_users_for_company(company_id=company_data.id)

    assert len(company_members) == 1
    assert company_members[0].id == user_member.id
    assert company_members[0].first_name == user_member.first_name
    assert company_members[0].last_name == user_member.last_name
    assert company_members[0].email == user_member.email
