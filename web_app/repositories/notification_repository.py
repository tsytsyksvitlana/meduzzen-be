from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.notification import Notification
from web_app.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession):
        super().__init__(Notification, session)

    async def get_notifications_by_user_and_status(
            self, user_id: int, status: str | None
    ) -> list[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)

        if status:
            query = query.where(Notification.status == status)

        result = await self.session.execute(query)
        notifications = result.scalars().all()
        return notifications
