from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.exceptions.notifications import NotificationNotFoundException
from web_app.exceptions.permission import PermissionDeniedException
from web_app.models import CompanyMembership, QuizParticipation
from web_app.repositories.company_repository import CompanyRepository
from web_app.repositories.notification_repository import NotificationRepository
from web_app.repositories.quiz_participation_repository import (
    QuizParticipationRepository
)
from web_app.repositories.quiz_repository import QuizRepository
from web_app.schemas.notification import NotificationStatus
from web_app.schemas.quiz import AnswerCreate, QuestionCreate, QuizCreate
from web_app.services.notification.notification_service import (
    NotificationService
)

pytestmark = pytest.mark.anyio


async def test_create_notification(
    db_session: AsyncSession, create_test_users
):
    user = create_test_users[0]
    notification_repository = NotificationRepository(db_session)
    quiz_repository = QuizRepository(db_session),
    company_repository = CompanyRepository(db_session),
    quiz_participation_repository = QuizParticipationRepository(db_session)
    notification_service = NotificationService(
        notification_repository,
        quiz_repository,
        company_repository,
        quiz_participation_repository,
    )

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
    notification_repository = NotificationRepository(db_session)
    quiz_repository = QuizRepository(db_session),
    company_repository = CompanyRepository(db_session),
    quiz_participation_repository = QuizParticipationRepository(db_session)
    notification_service = NotificationService(
        notification_repository,
        quiz_repository,
        company_repository,
        quiz_participation_repository,
    )

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
    notification_repository = NotificationRepository(db_session)
    quiz_repository = QuizRepository(db_session)
    company_repository = CompanyRepository(db_session)
    quiz_participation_repository = QuizParticipationRepository(db_session)
    notification_service = NotificationService(
        notification_repository,
        quiz_repository,
        company_repository,
        quiz_participation_repository,
    )

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


@pytest.fixture(scope="function")
async def setup_inactive_user_notification_test(
    db_session: AsyncSession,
    create_test_users,
    create_test_companies,
    quiz_service
):
    owner_user = create_test_users[0]
    member_user = create_test_users[1]
    test_company = create_test_companies[0]

    db_session.add(
        CompanyMembership(
            company_id=test_company.id,
            user_id=owner_user.id,
            role="Owner"
        )
    )
    db_session.add(
        CompanyMembership(
            company_id=test_company.id,
            user_id=member_user.id,
            role="Member"
        )
    )
    await db_session.commit()

    quiz_data = QuizCreate(
        title="General Knowledge Quiz",
        description="Test your knowledge",
        participation_frequency=10,
        company_id=test_company.id,
        questions=[
            QuestionCreate(
                title="What is the capital of France?",
                answers=[
                    AnswerCreate(text="Paris", is_correct=True),
                    AnswerCreate(text="London", is_correct=False)
                ]
            ),
            QuestionCreate(
                title="What is 2 + 2?",
                answers=[
                    AnswerCreate(text="4", is_correct=True),
                    AnswerCreate(text="5", is_correct=False)
                ]
            ),
            QuestionCreate(
                title="When is the independence day of Ukraine?",
                answers=[
                    AnswerCreate(text="24 August", is_correct=True),
                    AnswerCreate(text="28 July", is_correct=False)
                ]
            )
        ]
    )

    quiz = await quiz_service.create_quiz(quiz_data, current_user=owner_user)

    last_participation_date = datetime.now(timezone.utc) - timedelta(days=15)
    participation = QuizParticipation(
        quiz_id=quiz.id,
        user_id=member_user.id,
        score=5,
        total_questions=10,
        participated_at=last_participation_date,
        company_id=test_company.id,
    )
    db_session.add(participation)
    await db_session.commit()

    return {
        "owner_user": owner_user,
        "member_user": member_user,
        "company": test_company,
        "quiz": quiz,
        "participation": participation
    }


async def test_notify_inactive_users(
    db_session, setup_inactive_user_notification_test,
):
    notification_repository = NotificationRepository(db_session)
    quiz_repository = QuizRepository(db_session)
    company_repository = CompanyRepository(db_session)
    quiz_participation_repository = QuizParticipationRepository(db_session)

    notification_service = NotificationService(
        notification_repository,
        quiz_repository,
        company_repository,
        quiz_participation_repository,
    )

    member_user = setup_inactive_user_notification_test["member_user"]
    quiz = setup_inactive_user_notification_test["quiz"]

    await notification_service.notify_inactive_users()

    notifications = await notification_service.notification_repository.get_notifications_by_user_and_status(
        member_user.id, None
    )

    assert len(notifications) > 0, "No notifications were created for inactive user."

    assert any(
        f"Reminder: Quiz '{quiz.title}' is available for retake." in notification.message
        for notification in notifications
    ), "The expected notification message was not found."
