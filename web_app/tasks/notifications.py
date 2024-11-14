import logging

from web_app.services.notification.notification_service import (
    get_notification_service
)

logger = logging.getLogger(__name__)


async def task_notify_inactive_users():
    """
    Send notification to pass quiz when new attempt is available.
    """
    logger.info("Running notify_inactive_users task.")
    notification_service = get_notification_service()
    await notification_service.notify_inactive_users()
