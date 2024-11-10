from fastapi import APIRouter, Depends

from web_app.models import User
from web_app.services.notification.notification_service import (
    NotificationService,
    get_notification_service
)
from web_app.utils.auth import get_current_user

router = APIRouter()


@router.patch("/{notification_id}/mark_as_read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    notification = await notification_service.mark_as_read(
        notification_id, current_user
    )
    return notification


@router.get("/")
async def get_notifications(
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    notifications = await notification_service.get_user_notifications(
        status, current_user
    )
    return notifications
