from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.exceptions.notifications import NotificationNotFoundException
from web_app.exceptions.permission import PermissionDeniedException
from web_app.models.notification import Notification
from web_app.models.user import User
from web_app.repositories.notification_repository import NotificationRepository
from web_app.schemas.notification import NotificationStatus


class NotificationService:
    def __init__(
        self,
        notification_repository: NotificationRepository,
    ):
        self.notification_repository = notification_repository

    async def create_notification(self, user_id: int, message: str):
        notification = Notification(user_id=user_id, message=message)
        await self.notification_repository.create_obj(notification)
        await self.notification_repository.session.commit()

    async def get_user_notifications(self, status: str | None, current_user: User) -> list[Notification]:
        notifications = await self.notification_repository.get_notifications_by_user_and_status(
            current_user.id, status
        )
        return notifications

    async def mark_as_read(self, notification_id: int, current_user: User):
        notification = await self.notification_repository.get_obj_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundException(notification_id)
        if notification.user_id != current_user.id:
            raise PermissionDeniedException()
        notification.status = NotificationStatus.READ.value
        await self.notification_repository.update_obj(notification)
        await self.notification_repository.session.commit()


def get_notification_service(
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> NotificationService:
    return NotificationService(
        notification_repository=NotificationRepository(session=session),
    )
