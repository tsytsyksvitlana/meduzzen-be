import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.join_request import JoinRequest
from web_app.repositories.join_request_repository import JoinRequestRepository
from web_app.schemas.join_request import JoinRequestStatus

pytestmark = pytest.mark.anyio


async def test_create_join_request(
        db_session: AsyncSession, create_test_companies, create_test_users
):
    join_request_repository = JoinRequestRepository(session=db_session)
    company = create_test_companies[0]
    user = create_test_users[0]

    join_request_data = JoinRequest(
        company_id=company.id,
        user_id=user.id,
        status=JoinRequestStatus.PENDING.value
    )

    created_join_request = await join_request_repository.create_obj(join_request_data)
    await join_request_repository.session.commit()

    assert created_join_request.id is not None
    assert created_join_request.company_id == company.id
    assert created_join_request.user_id == user.id
    assert created_join_request.status == JoinRequestStatus.PENDING.value


async def test_get_join_request(
        db_session: AsyncSession, create_test_companies, create_test_users
):
    join_request_repository = JoinRequestRepository(session=db_session)
    company = create_test_companies[0]
    user = create_test_users[0]

    join_request_data = JoinRequest(
        company_id=company.id,
        user_id=user.id,
        status=JoinRequestStatus.PENDING.value
    )
    db_session.add(join_request_data)
    await db_session.commit()

    fetched_join_request = await join_request_repository.get_request(
        company.id, user.id
    )

    assert fetched_join_request is not None
    assert fetched_join_request.company_id == company.id
    assert fetched_join_request.user_id == user.id
    assert fetched_join_request.status == JoinRequestStatus.PENDING.value


async def test_get_user_join_requests(
        db_session: AsyncSession, create_test_companies, create_test_users
):
    join_request_repository = JoinRequestRepository(session=db_session)

    join_request_data_1 = JoinRequest(
        company_id=create_test_companies[0].id,
        user_id=create_test_users[0].id,
        status="Pending"
    )
    join_request_data_2 = JoinRequest(
        company_id=create_test_companies[1].id,
        user_id=create_test_users[0].id,
        status="Accepted"
    )
    db_session.add_all([join_request_data_1, join_request_data_2])
    await db_session.commit()

    user_join_requests = await join_request_repository.get_user_requests(create_test_users[0].id)

    assert len(user_join_requests) == 2
    assert user_join_requests[0].status == "Pending"
    assert user_join_requests[1].status == "Accepted"


async def test_get_pending_join_requests(
        db_session: AsyncSession, create_test_companies, create_test_users
):
    join_request_repository = JoinRequestRepository(session=db_session)
    company = create_test_companies[0]
    user1 = create_test_users[0]
    user2 = create_test_users[1]

    join_request_data_1 = JoinRequest(
        company_id=company.id,
        user_id=user1.id,
        status=JoinRequestStatus.PENDING.value
    )
    join_request_data_2 = JoinRequest(
        company_id=company.id,
        user_id=user2.id,
        status=JoinRequestStatus.ACCEPTED.value
    )
    db_session.add_all([join_request_data_1, join_request_data_2])
    await db_session.commit()

    pending_requests = await join_request_repository.get_pending_requests(company.id)

    assert len(pending_requests) == 1
    assert pending_requests[0].user_id == user1.id
    assert pending_requests[0].company_id == company.id
    assert pending_requests[0].status == JoinRequestStatus.PENDING.value


async def test_update_join_request_status(
        db_session: AsyncSession, create_test_companies, create_test_users
):
    join_request_repository = JoinRequestRepository(session=db_session)
    company = create_test_companies[0]
    user = create_test_users[0]

    join_request_data = JoinRequest(
        company_id=company.id,
        user_id=user.id,
        status=JoinRequestStatus.PENDING.value
    )
    db_session.add(join_request_data)
    await db_session.commit()

    join_request_data.status = JoinRequestStatus.ACCEPTED.value
    updated_join_request = await join_request_repository.update_obj(join_request_data)
    await db_session.commit()

    assert updated_join_request is not None
    assert updated_join_request.status == JoinRequestStatus.ACCEPTED.value

    fetched_join_request = await join_request_repository.get_request(
        company.id, user.id
    )
    assert fetched_join_request.status == JoinRequestStatus.ACCEPTED.value


async def test_delete_join_request(
        db_session: AsyncSession, create_test_companies, create_test_users
):
    join_request_repository = JoinRequestRepository(session=db_session)
    company = create_test_companies[0]
    user = create_test_users[0]

    join_request_data = JoinRequest(
        company_id=company.id,
        user_id=user.id,
        status=JoinRequestStatus.PENDING.value
    )
    db_session.add(join_request_data)
    await db_session.commit()

    deleted_join_request = await join_request_repository.delete_obj(join_request_data.id)
    await join_request_repository.session.commit()

    assert deleted_join_request.id == join_request_data.id
    assert await join_request_repository.get_request(
        company.id, user.id
    ) is None
