import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.exceptions.notifications import NotificationNotFoundException
from web_app.exceptions.permission import PermissionDeniedException
from web_app.repositories.notification_repository import NotificationRepository
from web_app.schemas.notification import NotificationStatus
from web_app.services.notification.notification_service import (
    NotificationService
)

pytestmark = pytest.mark.anyio


async def test_create_notification(
    db_session: AsyncSession, create_test_users
):
    user = create_test_users[0]
    notification_repository = NotificationRepository(session=db_session)
    notification_service = NotificationService(notification_repository)

    message = "You have a new quiz!"
    await notification_service.create_notification(user.id, message)

    notifications = await notification_repository.get_notifications_by_user_and_status(
        user.id, None
    )
    assert len(notifications) == 1
    assert notifications[0].message == message
    assert notifications[0].user_id == user.id


async def test_get_user_notifications(
    db_session: AsyncSession, create_test_users, create_test_notifications
):
    user = create_test_users[0]
    notification_repository = NotificationRepository(session=db_session)
    notification_service = NotificationService(notification_repository)

    notifications = await notification_service.get_user_notifications(None, user)

    assert len(notifications) == len(create_test_notifications)

    notifications = await notification_service.get_user_notifications(
        NotificationStatus.UNREAD.value, user
    )
    unread_notifications = [
        n for n in notifications if n.status == NotificationStatus.UNREAD.value
    ]
    assert len(notifications) == len(unread_notifications)


async def test_mark_notification_as_read(
    db_session: AsyncSession, create_test_users, create_test_notifications
):
    user = create_test_users[0]
    notification_repository = NotificationRepository(session=db_session)
    notification_service = NotificationService(notification_repository)

    notification = create_test_notifications[0]
    assert notification.status == NotificationStatus.UNREAD.value

    await notification_service.mark_as_read(notification.id, user)

    updated_notification = await notification_repository.get_obj_by_id(
        notification.id
    )
    assert updated_notification.status == NotificationStatus.READ.value

    another_user = create_test_users[1]
    with pytest.raises(PermissionDeniedException):
        await notification_service.mark_as_read(notification.id, another_user)

    with pytest.raises(NotificationNotFoundException):
        await notification_service.mark_as_read(999, user)
