import logging

from web_app.repositories.company_repository import CompanyRepository
from web_app.repositories.notification_repository import NotificationRepository
from web_app.repositories.quiz_participation_repository import QuizParticipationRepository
from web_app.repositories.quiz_repository import QuizRepository
from web_app.services.notification.notification_service import NotificationService
from web_app.db.postgres_helper import postgres_helper as pg_helper

logger = logging.getLogger(__name__)


async def task_notify_inactive_users():
    """
    Send notification to pass quiz when new attempt is available.
    """
    logger.info("Running notify_inactive_users task.")
    notification_service = NotificationService(
        notification_repository=NotificationRepository(pg_helper.session_getter()),
        quiz_repository=QuizRepository(pg_helper.session_getter()),
        company_repository=CompanyRepository(pg_helper.session_getter()),
        quiz_participation_repository=QuizParticipationRepository(pg_helper.session_getter())
    )
    await notification_service.notify_inactive_users()
