import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.exceptions.permission import PermissionDeniedException
from web_app.exceptions.quizzes import QuizNotFoundException
from web_app.exceptions.validation import InvalidFieldException
from web_app.models import CompanyMembership
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.repositories.question_repository import QuestionRepository
from web_app.repositories.quiz_repository import QuizRepository
from web_app.schemas.quiz import (
    AnswerCreate,
    QuestionCreate,
    QuizCreate,
    QuizUpdate
)
from web_app.services.quizzes.quiz_service import QuizService

pytestmark = pytest.mark.anyio


async def test_quiz_service_create_quiz(
        db_session: AsyncSession,
        create_test_users,
        create_test_companies
):
    create_test_company = create_test_companies[0]
    quiz_repository = QuizRepository(session=db_session)
    question_repository = QuestionRepository(session=db_session)
    company_repository = CompanyRepository(session=db_session)
    membership_repository = CompanyMembershipRepository(session=db_session)

    quiz_service = QuizService(
        quiz_repository=quiz_repository,
        question_repository=question_repository,
        company_repository=company_repository,
        membership_repository=membership_repository
    )

    user = create_test_users[0]
    company_id = create_test_company.id

    company_membership = CompanyMembership(
        company_id=company_id,
        user_id=user.id,
        role="Owner",
    )
    db_session.add(company_membership)
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
                    AnswerCreate(
                        text="Paris",
                        is_correct=True,
                    ),
                    AnswerCreate(
                        text="London",
                        is_correct=False,
                    )
                ]
            ),
            QuestionCreate(
                title="What is 2 + 2?",
                answers=[
                    AnswerCreate(
                        text="4",
                        is_correct=True,
                    ),
                    AnswerCreate(
                        text="5",
                        is_correct=False,
                    )
                ]
            )
        ]
    )

    await quiz_service.check_is_owner_or_admin(company_id=company_id, user=user)

    created_quiz = await quiz_service.create_quiz(quiz_data, current_user=user)

    assert created_quiz.title == quiz_data.title
    assert len(created_quiz.questions) == 2
    assert len(created_quiz.questions[0].answers) == 2

    another_user = create_test_users[1]
    with pytest.raises(PermissionDeniedException):
        await quiz_service.check_is_owner_or_admin(company_id=company_id, user=another_user)

    invalid_quiz_data = QuizCreate(
        title="Invalid Quiz",
        description="This quiz has only one question",
        participation_frequency=10,
        company_id=company_id,
        questions=[
            QuestionCreate(
                title="What is the capital of Germany?",
                answers=[
                    AnswerCreate(
                        text="Paris",
                        is_correct=True,
                    )
                ]
            )
        ]
    )
    with pytest.raises(InvalidFieldException):
        await quiz_service.create_quiz(invalid_quiz_data, current_user=user)


async def test_quiz_service_check_is_owner_or_admin(
        db_session: AsyncSession,
        create_test_users,
        create_test_companies
):
    create_test_company = create_test_companies[0]
    quiz_repository = QuizRepository(session=db_session)
    question_repository = QuestionRepository(session=db_session)
    company_repository = CompanyRepository(session=db_session)
    membership_repository = CompanyMembershipRepository(session=db_session)

    quiz_service = QuizService(
        quiz_repository=quiz_repository,
        question_repository=question_repository,
        company_repository=company_repository,
        membership_repository=membership_repository
    )

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
        create_test_companies
):
    create_test_company = create_test_companies[0]
    quiz_repository = QuizRepository(session=db_session)
    question_repository = QuestionRepository(session=db_session)
    company_repository = CompanyRepository(session=db_session)
    membership_repository = CompanyMembershipRepository(session=db_session)

    quiz_service = QuizService(
        quiz_repository=quiz_repository,
        question_repository=question_repository,
        company_repository=company_repository,
        membership_repository=membership_repository
    )

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
                    {
                        "title": "What is 2+2?",
                        "answers": [
                            {"text": "4", "is_correct": True},
                            {"text": "5", "is_correct": False}
                        ]
                    }
                ]
            ),
            current_user=user
        )


async def test_quiz_service_get_quizzes_for_company(
        db_session: AsyncSession,
        create_test_users,
        create_test_companies,
        create_test_quizzes
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
):
    quizzes = create_test_quizzes
    user = create_test_users[0]
    another_user = create_test_users[1]

    quiz_repository = QuizRepository(session=db_session)
    question_repository = QuestionRepository(session=db_session)
    company_repository = CompanyRepository(session=db_session)
    membership_repository = CompanyMembershipRepository(session=db_session)

    quiz_service = QuizService(
        quiz_repository=quiz_repository,
        question_repository=question_repository,
        company_repository=company_repository,
        membership_repository=membership_repository
    )

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
        create_test_quizzes
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

    quiz_service = QuizService(
        quiz_repository=QuizRepository(session=db_session),
        question_repository=QuestionRepository(session=db_session),
        company_repository=CompanyRepository(session=db_session),
        membership_repository=CompanyMembershipRepository(session=db_session)
    )

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
        create_test_quizzes
):
    user = create_test_users[0]
    quiz = create_test_quizzes[0]
    question = quiz.questions[0]

    quiz_service = QuizService(
        quiz_repository=QuizRepository(session=db_session),
        question_repository=QuestionRepository(session=db_session),
        company_repository=CompanyRepository(session=db_session),
        membership_repository=CompanyMembershipRepository(session=db_session)
    )

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
        create_test_companies
):
    user = create_test_users[0]
    company_id = create_test_companies[0].id
    quiz = create_test_quizzes[0]

    company_membership = CompanyMembership(
        company_id=company_id,
        user_id=user.id,
        role="Owner"
    )
    db_session.add(company_membership)
    await db_session.commit()

    quiz_service = QuizService(
        quiz_repository=QuizRepository(session=db_session),
        question_repository=QuestionRepository(session=db_session),
        company_repository=CompanyRepository(session=db_session),
        membership_repository=CompanyMembershipRepository(session=db_session)
    )

    question_data = QuestionCreate(
        title="What is the largest planet?",
        answers=[
            AnswerCreate(text="Jupiter", is_correct=True),
            AnswerCreate(text="Saturn", is_correct=False)
        ]
    )

    question = await quiz_service.add_question_to_quiz(
        quiz_id=quiz.id,
        question_data=question_data,
        current_user=user
    )
    assert question.title == question_data.title
    assert len(question.answers) == 2

    invalid_question_data = QuestionCreate(
        title="What is the capital of Germany?",
        answers=[AnswerCreate(text="Berlin", is_correct=True)]
    )
    with pytest.raises(InvalidFieldException):
        await quiz_service.add_question_to_quiz(
            quiz_id=quiz.id,
            question_data=invalid_question_data,
            current_user=user
        )

    another_user = create_test_users[1]
    with pytest.raises(PermissionDeniedException):
        await quiz_service.add_question_to_quiz(
            quiz_id=quiz.id,
            question_data=question_data,
            current_user=another_user
        )
