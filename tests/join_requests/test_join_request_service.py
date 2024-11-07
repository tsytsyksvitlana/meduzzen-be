import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.exceptions.join_requests import (
    JoinRequestAlreadyExistsException,
    JoinRequestNotFoundException
)
from web_app.exceptions.permission import PermissionDeniedException
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.repositories.join_request_repository import JoinRequestRepository
from web_app.schemas.roles import Role
from web_app.services.join_requests.join_request_service import (
    JoinRequestService
)

pytestmark = pytest.mark.anyio


@pytest.fixture
async def join_request_service(db_session: AsyncSession):
    join_request_repository = JoinRequestRepository(session=db_session)
    membership_repository = CompanyMembershipRepository(session=db_session)
    company_repository = CompanyRepository(session=db_session)
    return JoinRequestService(
        join_request_repository, membership_repository, company_repository
    )


async def test_request_to_join(
    join_request_service: JoinRequestService,
    db_session: AsyncSession,
    create_test_users,
    create_test_companies
):
    user = create_test_users[0]
    company = create_test_companies[0]

    join_request = await join_request_service.request_to_join(company.id, user.id)

    assert join_request.company_id == company.id
    assert join_request.user_id == user.id

    with pytest.raises(JoinRequestAlreadyExistsException):
        await join_request_service.request_to_join(company.id, user.id)


async def test_cancel_request(
    join_request_service: JoinRequestService,
    db_session: AsyncSession,
    create_test_users,
    create_test_companies
):
    user = create_test_users[0]
    company = create_test_companies[0]

    join_request = await join_request_service.request_to_join(company.id, user.id)
    await join_request_service.cancel_request(join_request.id, user.id)

    with pytest.raises(JoinRequestNotFoundException):
        await join_request_service.cancel_request(join_request.id, user.id)


async def test_accept_request(
    join_request_service: JoinRequestService,
    db_session: AsyncSession,
    create_test_users,
    create_test_companies
):
    owner = create_test_users[0]
    user = create_test_users[1]
    company = create_test_companies[0]

    await join_request_service.request_to_join(company.id, user.id)
    await join_request_service.accept_request(1, owner.id)

    membership = await join_request_service.membership_repository \
        .get_user_company_membership(
            company_id=company.id, user_id=user.id
        )
    assert membership is not None

    with pytest.raises(JoinRequestNotFoundException):
        await join_request_service.accept_request(1, owner.id)


async def test_decline_request(
    join_request_service: JoinRequestService,
    db_session: AsyncSession,
    create_test_users,
    create_test_companies
):
    owner = create_test_users[0]
    user = create_test_users[1]
    company = create_test_companies[0]

    join_request = await join_request_service.request_to_join(company.id, user.id)
    await join_request_service.decline_request(join_request.id, owner.id)

    with pytest.raises(JoinRequestNotFoundException):
        await join_request_service.decline_request(join_request.id, owner.id)


async def test_get_user_requests(
    join_request_service: JoinRequestService,
    db_session: AsyncSession,
    create_test_users,
    create_test_companies
):
    user = create_test_users[0]
    company = create_test_companies[0]

    join_request = await join_request_service.request_to_join(company.id, user.id)
    user_requests = await join_request_service.get_user_requests(user.id, user.id)

    assert len(user_requests) == 1
    assert user_requests[0].id == join_request.id

    with pytest.raises(PermissionDeniedException):
        await join_request_service.get_user_requests(user.id, create_test_users[1].id)


async def test_get_pending_requests(
    join_request_service: JoinRequestService,
    db_session: AsyncSession,
    create_test_users,
    create_test_companies
):
    owner = create_test_users[0]
    user = create_test_users[1]
    company = create_test_companies[0]

    await join_request_service.membership_repository.add_user_to_company(
        company_id=company.id,
        user_id=owner.id,
        role=Role.OWNER.value
    )

    await join_request_service.request_to_join(company.id, user.id)
    pending_requests = await join_request_service.get_pending_requests(
        company.id, owner.id
    )

    assert len(pending_requests) == 1
    assert pending_requests[0].user_id == user.id

    with pytest.raises(PermissionDeniedException):
        await join_request_service.get_pending_requests(company.id, user.id)
