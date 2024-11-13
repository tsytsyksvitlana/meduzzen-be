import asyncio
from datetime import datetime
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.exceptions.data import DataNotFoundException
from web_app.exceptions.permission import PermissionDeniedException
from web_app.exceptions.quizzes import (
    AnswerNotFoundException,
    QuestionNotFoundException,
    QuizNotFoundException
)
from web_app.exceptions.validation import InvalidFieldException
from web_app.models import CompanyMembership
from web_app.schemas.quiz import (
    AnswerCreate,
    QuestionCreate,
    QuizCreate,
    QuizParticipationSchema,
    QuizUpdate
)
from web_app.schemas.roles import Role
from web_app.services.quizzes.quiz_service import QuizService

pytestmark = pytest.mark.anyio


async def test_quiz_service_create_quiz(
    db_session: AsyncSession,
    create_test_users,
    create_test_companies,
    quiz_service: QuizService,
):
    create_test_company = create_test_companies[0]
    user_owner = create_test_users[0]
    user_member = create_test_users[1]
    company_id = create_test_company.id

    owner_membership = CompanyMembership(
        company_id=company_id,
        user_id=user_owner.id,
        role=Role.OWNER.value,
    )
    member_membership = CompanyMembership(
        company_id=company_id,
        user_id=user_member.id,
        role=Role.MEMBER.value,
    )
    db_session.add_all([owner_membership, member_membership])
    await db_session.commit()

    quiz_data = QuizCreate(
        title="General Knowledge Quiz",
        description="Test your knowledge",
        participation_frequency=10,
        company_id=company_id,
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
            )
        ]
    )

    await quiz_service.check_is_owner_or_admin(company_id=company_id, user=user_owner)

    created_quiz = await quiz_service.create_quiz(quiz_data, current_user=user_owner)

    assert created_quiz.title == quiz_data.title
    assert len(created_quiz.questions) == 2
    assert len(created_quiz.questions[0].answers) == 2

    notification = await quiz_service.notification_repository.get_notifications_by_user_and_status(
        user_member.id, None
    )
    assert notification is not None

    with pytest.raises(PermissionDeniedException):
        await quiz_service.check_is_owner_or_admin(company_id=company_id, user=user_member)

    invalid_quiz_data = QuizCreate(
        title="Invalid Quiz",
        description="This quiz has only one question",
        participation_frequency=10,
        company_id=company_id,
        questions=[
            QuestionCreate(
                title="What is the capital of Germany?",
                answers=[AnswerCreate(text="Paris", is_correct=True)]
            )
        ]
    )
    with pytest.raises(InvalidFieldException):
        await quiz_service.create_quiz(invalid_quiz_data, current_user=user_owner)


async def test_quiz_service_check_is_owner_or_admin(
    db_session: AsyncSession,
    create_test_users,
    create_test_companies,
    quiz_service: QuizService
):
    create_test_company = create_test_companies[0]
    user = create_test_users[0]
    company_id = create_test_company.id

    company_membership = CompanyMembership(
        company_id=company_id,
        user_id=user.id,
        role="Owner",
    )
    db_session.add(company_membership)
    await db_session.commit()
    await quiz_service.check_is_owner_or_admin(company_id=company_id, user=user)

    another_user = create_test_users[1]
    with pytest.raises(PermissionDeniedException):
        await quiz_service.check_is_owner_or_admin(company_id=company_id, user=another_user)


async def test_quiz_service_create_quiz_with_invalid_permissions(
    db_session: AsyncSession,
    create_test_users,
    create_test_companies,
    quiz_service: QuizService
):
    create_test_company = create_test_companies[0]
    user = create_test_users[0]
    company_id = create_test_company.id

    with pytest.raises(PermissionDeniedException):
        await quiz_service.create_quiz(
            QuizCreate(
                title="Test Quiz",
                description="A new test quiz",
                participation_frequency=10,
                company_id=company_id,
                questions=[
                    QuestionCreate(
                        title="What is 2+2?",
                        answers=[
                            AnswerCreate(text="4", is_correct=True),
                            AnswerCreate(text="5", is_correct=False)
                        ]
                    )
                ]
            ),
            current_user=user
        )


async def test_quiz_service_get_quizzes_for_company(
    db_session: AsyncSession,
    create_test_users,
    create_test_companies,
    create_test_quizzes,
    quiz_service: QuizService
):
    create_test_company = create_test_companies[0]
    company_id = create_test_company.id

    quizzes = create_test_quizzes

    assert len(quizzes) == 2
    assert quizzes[0].title == "General Knowledge Quiz"
    assert quizzes[1].title == "Math Quiz"

    for quiz in quizzes:
        assert quiz.company_id == company_id


async def test_quiz_service_delete_quiz(
    db_session: AsyncSession,
    create_test_quizzes,
    create_test_users,
    quiz_service: QuizService
):
    quizzes = create_test_quizzes
    user = create_test_users[0]
    another_user = create_test_users[1]

    assert len(quizzes) == 2

    await quiz_service.delete_quiz(quiz_id=quizzes[0].id, current_user=user)
    await quiz_service.quiz_repository.session.commit()

    with pytest.raises(QuizNotFoundException):
        await quiz_service.delete_quiz(quiz_id=quizzes[0].id, current_user=user)

    with pytest.raises(PermissionDeniedException):
        await quiz_service.delete_quiz(quiz_id=quizzes[1].id, current_user=another_user)

    await quiz_service.delete_quiz(quiz_id=quizzes[1].id, current_user=user)
    await quiz_service.quiz_repository.session.commit()

    with pytest.raises(QuizNotFoundException):
        await quiz_service.delete_quiz(quiz_id=quizzes[0].id, current_user=user)


async def test_update_quiz(
    db_session: AsyncSession,
    create_test_users,
    create_test_quizzes,
    quiz_service: QuizService
):
    user = create_test_users[0]
    quiz = create_test_quizzes[0]

    company_membership = CompanyMembership(
        company_id=quiz.company_id,
        user_id=user.id,
        role="Owner"
    )
    db_session.add(company_membership)
    await db_session.commit()

    quiz_update_data = QuizUpdate(
        title="Updated Quiz Title",
        description="Updated description",
        participation_frequency=5
    )

    updated_quiz = await quiz_service.update_quiz(
        quiz_id=quiz.id,
        quiz_data=quiz_update_data,
        current_user=user
    )
    assert updated_quiz.title == quiz_update_data.title
    assert updated_quiz.description == quiz_update_data.description
    assert updated_quiz.participation_frequency == quiz_update_data.participation_frequency

    another_user = create_test_users[1]
    with pytest.raises(PermissionDeniedException):
        await quiz_service.update_quiz(
            quiz_id=quiz.id,
            quiz_data=quiz_update_data,
            current_user=another_user
        )

    with pytest.raises(QuizNotFoundException):
        await quiz_service.update_quiz(
            quiz_id=99999,
            quiz_data=quiz_update_data,
            current_user=user
        )


async def test_delete_question_from_quiz(
    db_session: AsyncSession,
    create_test_users,
    create_test_quizzes,
    quiz_service: QuizService
):
    user = create_test_users[0]
    quiz = create_test_quizzes[0]
    question = quiz.questions[0]

    await quiz_service.delete_question_from_quiz(
        quiz_id=quiz.id,
        question_id=question.id,
        current_user=user
    )
    remaining_questions = await quiz_service.question_repository.get_questions_for_quiz(quiz.id)
    assert len(remaining_questions) == 2

    question_to_delete = quiz.questions[1]
    with pytest.raises(InvalidFieldException):
        await quiz_service.delete_question_from_quiz(
            quiz_id=quiz.id,
            question_id=question_to_delete.id,
            current_user=user
        )

    another_user = create_test_users[1]
    with pytest.raises(PermissionDeniedException):
        await quiz_service.delete_question_from_quiz(
            quiz_id=quiz.id,
            question_id=question.id,
            current_user=another_user
        )


async def test_add_question_to_quiz(
    db_session: AsyncSession,
    create_test_users,
    create_test_quizzes,
    create_test_companies,
    quiz_service: QuizService
):
    user = create_test_users[0]
    quiz = create_test_quizzes[0]

    company_membership = CompanyMembership(
        company_id=quiz.company_id,
        user_id=user.id,
        role="Owner",
    )
    db_session.add(company_membership)
    await db_session.commit()

    question_data = QuestionCreate(
        title="What is the capital of Spain?",
        answers=[
            AnswerCreate(text="Madrid", is_correct=True),
            AnswerCreate(text="Barcelona", is_correct=False)
        ]
    )
    question = await quiz_service.add_question_to_quiz(
        quiz_id=quiz.id,
        question_data=question_data,
        current_user=user
    )
    assert question.title == question_data.title
    assert len(question.answers) == len(question_data.answers)

    another_user = create_test_users[1]
    with pytest.raises(PermissionDeniedException):
        await quiz_service.add_question_to_quiz(
            quiz_id=quiz.id,
            question_data=question_data,
            current_user=another_user
        )

    with pytest.raises(QuizNotFoundException):
        await quiz_service.add_question_to_quiz(
            quiz_id=99999,
            question_data=question_data,
            current_user=user
        )


async def test_user_quiz_participation(
    db_session, create_test_users, create_test_quizzes, quiz_service: QuizService, mock_redis
):
    user = create_test_users[0]
    quiz = create_test_quizzes[0]
    quiz_id = quiz.id

    user_answers = [
        {
            "question_id": quiz.questions[0].id,
            "answer_id": quiz.questions[0].answers[0].id
        },
        {
            "question_id": quiz.questions[1].id,
            "answer_id": quiz.questions[1].answers[0].id
        },
        {
            "question_id": quiz.questions[2].id,
            "answer_id": quiz.questions[2].answers[0].id
        }
    ]
    quiz_participation = QuizParticipationSchema(
        user_answers=user_answers, quiz_id=quiz_id
    )

    participation = await quiz_service.user_quiz_participation(quiz_participation, user)

    assert participation.quiz_id == quiz_id
    assert participation.user_id == user.id
    assert participation.score == 3
    assert participation.total_questions == 3

    invalid_quiz_participation = QuizParticipationSchema(
        user_answers=user_answers, quiz_id=99999
    )
    with pytest.raises(QuizNotFoundException):
        await quiz_service.user_quiz_participation(invalid_quiz_participation, user)

    invalid_question_answer = [
        {
            "question_id": 9999,
            "answer_id": quiz.questions[0].answers[0].id
        }
    ]
    invalid_question_participation = QuizParticipationSchema(
        user_answers=invalid_question_answer, quiz_id=quiz.id
    )
    with pytest.raises(QuestionNotFoundException):
        await quiz_service.user_quiz_participation(invalid_question_participation, user)

    invalid_answer = [
        {
            "question_id": quiz.questions[0].id,
            "answer_id": 9999
        }
    ]
    invalid_answer_participation = QuizParticipationSchema(
        user_answers=invalid_answer, quiz_id=quiz.id
    )
    with pytest.raises(AnswerNotFoundException):
        await quiz_service.user_quiz_participation(invalid_answer_participation, user)


@pytest.mark.asyncio
async def test_create_quiz_participate_redis(
    db_session,
    create_test_users,
    create_test_quizzes,
    quiz_service: QuizService,
    mock_redis
):
    async def test():
        user = create_test_users[0]
        quiz = create_test_quizzes[0]
        quiz_id = quiz.id

        user_answers = [
            {"question_id": quiz.questions[0].id, "answer_id": quiz.questions[0].answers[0].id},
            {"question_id": quiz.questions[1].id, "answer_id": quiz.questions[1].answers[0].id},
            {"question_id": quiz.questions[2].id, "answer_id": quiz.questions[2].answers[0].id}
        ]

        quiz_participation_data = QuizParticipationSchema(
            quiz_id=quiz_id,
            user_answers=user_answers
        )

        with patch("web_app.db.redis_helper.redis_helper", mock_redis):
            participation = await quiz_service.user_quiz_participation(quiz_participation_data, user)

            assert participation.quiz_id == quiz_id
            assert participation.user_id == user.id
            assert participation.score == 3
            assert participation.total_questions == 3

            redis_key = f"quiz:{quiz_id}:user:{user.id}"
            redis_data = await mock_redis.get(redis_key)
            assert redis_data is not None

        invalid_quiz_participation = QuizParticipationSchema(
            quiz_id=99999,
            user_answers=user_answers
        )
        with pytest.raises(QuizNotFoundException):
            await quiz_service.user_quiz_participation(invalid_quiz_participation, user)

        invalid_question_answer = [{"question_id": 9999, "answer_id": quiz.questions[0].answers[0].id}]
        invalid_question_participation = QuizParticipationSchema(
            quiz_id=quiz_id,
            user_answers=invalid_question_answer
        )
        with pytest.raises(QuestionNotFoundException):
            await quiz_service.user_quiz_participation(invalid_question_participation, user)

        invalid_answer = [{"question_id": quiz.questions[0].id, "answer_id": 9999}]
        invalid_answer_participation = QuizParticipationSchema(
            quiz_id=quiz_id,
            user_answers=invalid_answer
        )
        with pytest.raises(AnswerNotFoundException):
            await quiz_service.user_quiz_participation(invalid_answer_participation, user)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test())


async def test_get_company_average_scores_over_time(
    create_test_users,
    create_test_quizzes,
    create_test_quiz_participations,
    quiz_service: QuizService
):
    user = create_test_users[0]
    quiz = create_test_quizzes[0]
    company_id = quiz.company_id

    result = await quiz_service.get_company_average_scores_over_time(
        company_id, user
    )

    assert len(result) == 1
    assert result[0].time_period == "2024-09"
    assert result[0].average_score == 80.0


async def test_get_user_detailed_quiz_scores_for_company(
    create_test_users,
    create_test_quizzes,
    create_test_quiz_participations,
    quiz_service: QuizService
):
    user = create_test_users[0]
    quiz = create_test_quizzes[0]
    company_id = quiz.company_id

    result = await quiz_service.get_user_detailed_quiz_scores_for_company(
        company_id, user.id, user
    )

    assert len(result) == 2
    assert result[0].quiz_id == quiz.id
    assert "2024-09" in result[0].scores_by_month
    assert result[0].scores_by_month["2024-09"] == 85.0


async def test_get_company_users_last_quiz_attempts(
    create_test_users,
    create_test_quizzes,
    create_test_quiz_participations,
    quiz_service: QuizService
):
    user = create_test_users[0]
    quiz = create_test_quizzes[0]
    company_id = quiz.company_id

    result = await quiz_service.get_company_users_last_quiz_attempts(
        company_id, user
    )

    assert len(result) == 1
    assert result[0].user_id == user.id
    assert result[0].last_attempt_at.replace(tzinfo=None) == datetime(
        2024, 9, 15, 0, 0
    )


async def test_get_user_overall_rating(
    create_test_users,
    create_test_quizzes,
    create_test_quiz_participations,
    quiz_service: QuizService
):
    user = create_test_users[0]

    result = await quiz_service.get_user_overall_rating(user.id)

    assert result.user_id == user.id
    assert result.overall_rating == 80.0


async def test_get_user_quiz_scores_with_time(
    create_test_users,
    create_test_quizzes,
    create_test_quiz_participations,
    quiz_service: QuizService
):
    user = create_test_users[0]
    quiz = create_test_quizzes[0]

    result = await quiz_service.get_user_quiz_scores_with_time(user.id)

    assert len(result) == 2
    assert result[0].quiz_id == quiz.id
    assert "2024-09" in result[0].scores_by_month
    assert result[0].scores_by_month["2024-09"].average == 85.0


async def test_get_user_last_quiz_participations(
    create_test_users,
    create_test_quizzes,
    create_test_quiz_participations,
    quiz_service: QuizService
):
    user = create_test_users[0]
    quiz_1 = create_test_quizzes[0]
    quiz_2 = create_test_quizzes[1]

    result = await quiz_service.get_user_last_quiz_participations(user.id)

    assert len(result) == 2
    assert result[0].quiz_id == quiz_1.id
    assert result[0].quiz_title == quiz_1.title
    assert result[0].last_participation_at == datetime(2024, 9, 15)

    assert result[1].quiz_id == quiz_2.id
    assert result[1].quiz_title == quiz_2.title
    assert result[1].last_participation_at == datetime(2024, 9, 10)

    user_no_participation = create_test_users[1]

    with pytest.raises(
            DataNotFoundException,
            match="No quiz participations found for this user"
    ):
        await quiz_service.get_user_last_quiz_participations(
            user_no_participation.id
        )
