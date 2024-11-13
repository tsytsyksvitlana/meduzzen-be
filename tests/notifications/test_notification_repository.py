import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.repositories.notification_repository import NotificationRepository
from web_app.schemas.notification import NotificationStatus

pytestmark = pytest.mark.anyio


async def test_get_notifications_by_user_and_status(
    db_session: AsyncSession, create_test_notifications, create_test_users
):
    user = create_test_users[0]
    notification_repository = NotificationRepository(session=db_session)

    notifications = await notification_repository.get_notifications_by_user_and_status(
        user.id, None
    )
    assert len(notifications) == len(create_test_notifications)
    assert all(notification.user_id == user.id for notification in notifications)

    unread_notifications = await notification_repository.get_notifications_by_user_and_status(
        user.id, NotificationStatus.UNREAD.value
    )
    assert len(unread_notifications) == 2
    assert all(
        notification.status == NotificationStatus.UNREAD.value
        for notification in unread_notifications
    )

    read_notifications = await notification_repository.get_notifications_by_user_and_status(
        user.id, NotificationStatus.READ.value
    )
    assert len(read_notifications) == 1
    assert all(
        notification.status == NotificationStatus.READ.value
        for notification in read_notifications
    )
