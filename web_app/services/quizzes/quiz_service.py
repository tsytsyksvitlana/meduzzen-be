from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.exceptions.companies import CompanyNotFoundException
from web_app.exceptions.permission import PermissionDeniedException
from web_app.exceptions.quizzes import (
    QuestionNotFoundException,
    QuizNotFoundException
)
from web_app.exceptions.validation import InvalidFieldException
from web_app.models import User
from web_app.models.answer import Answer
from web_app.models.question import Question
from web_app.models.quiz import Quiz
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.repositories.question_repository import QuestionRepository
from web_app.repositories.quiz_repository import QuizRepository
from web_app.schemas.quiz import QuestionCreate, QuizCreate, QuizUpdate
from web_app.schemas.roles import Role


class QuizService:
    def __init__(
        self,
        quiz_repository: QuizRepository,
        question_repository: QuestionRepository,
        company_repository: CompanyRepository,
        membership_repository: CompanyMembershipRepository
    ):
        self.quiz_repository = quiz_repository
        self.question_repository = question_repository
        self.membership_repository = membership_repository
        self.company_repository = company_repository

    async def check_is_owner_or_admin(self, company_id: int, user: User):
        membership = await self.membership_repository.get_user_company_membership(
            company_id=company_id, user_id=user.id
        )
        if not membership or not (
                membership.role == Role.OWNER.value or membership.role == Role.ADMIN.value
        ):
            raise PermissionDeniedException()

    async def create_quiz(self, quiz_data: QuizCreate, current_user: User):
        exists_company = await self.company_repository.get_obj_by_id(company_id=quiz_data.company_id)
        if not exists_company:
            raise CompanyNotFoundException(company_id=quiz_data.company_id)
        await self.check_is_owner_or_admin(quiz_data.company_id, current_user)
        if not quiz_data.questions or len(quiz_data.questions) < 2:
            raise InvalidFieldException(
                "The quiz must have at least two questions."
            )

        for question_data in quiz_data.questions:
            if len(question_data.answers) < 2:
                raise InvalidFieldException(
                    f"Question '{question_data.title}' must have at least two answers."
                )

        quiz = Quiz(
            title=quiz_data.title,
            description=quiz_data.description,
            participation_frequency=quiz_data.participation_frequency,
            company_id=quiz_data.company_id,
        )

        for question_data in quiz_data.questions:
            question = Question(title=question_data.title, quiz_id=quiz.id)
            quiz.questions.append(question)

            question.answers = [
                Answer(text=answer_data.text, is_correct=answer_data.is_correct)
                for answer_data in question_data.answers
            ]

        await self.quiz_repository.create_obj(quiz)
        await self.quiz_repository.session.commit()

        return quiz

    async def update_quiz(self, quiz_id: int, quiz_data: QuizUpdate, current_user: User):
        quiz = await self.quiz_repository.get_obj_by_id(quiz_id)
        if not quiz:
            raise QuizNotFoundException(quiz_id)

        await self.check_is_owner_or_admin(quiz.company_id, current_user)

        quiz.title = quiz_data.title
        quiz.description = quiz_data.description
        quiz.participation_frequency = quiz_data.participation_frequency

        await self.quiz_repository.update_obj(quiz)
        await self.quiz_repository.session.commit()
        return quiz

    async def get_quizzes_for_company(self, company_id, skip, limit):
        exists_company = await self.company_repository.get_obj_by_id(company_id)
        if not exists_company:
            raise CompanyNotFoundException(company_id)
        quizzes = await self.quiz_repository.get_objs(company_id, skip, limit)
        return quizzes

    async def delete_quiz(self, quiz_id: int, current_user: User):
        quiz = await self.quiz_repository.get_obj_by_id(quiz_id)
        if not quiz:
            raise QuizNotFoundException(quiz_id)

        await self.check_is_owner_or_admin(quiz.company_id, current_user)

        await self.quiz_repository.delete_obj(quiz_id)
        await self.quiz_repository.session.commit()

    async def add_question_to_quiz(
        self,
        quiz_id: int,
        question_data: QuestionCreate,
        current_user: User
    ):
        quiz = await self.quiz_repository.get_obj_by_id(quiz_id)
        if not quiz:
            raise QuizNotFoundException(quiz_id)
        await self.check_is_owner_or_admin(quiz.company_id, current_user)

        if len(question_data.answers) < 2:
            raise InvalidFieldException(
                f"Question '{question_data.title}' must have at least two answers."
            )

        question = Question(title=question_data.title, quiz_id=quiz_id)
        await self.question_repository.create_obj(question)

        question.answers = [
            Answer(text=answer_data.text, is_correct=answer_data.is_correct)
            for answer_data in question_data.answers
        ]

        await self.quiz_repository.session.commit()

        return question

    async def delete_question_from_quiz(
        self,
        quiz_id: int,
        question_id: int,
        current_user: User
    ):
        quiz = await self.quiz_repository.get_obj_by_id(quiz_id)
        if not quiz:
            raise QuizNotFoundException(quiz_id)
        await self.check_is_owner_or_admin(quiz.company_id, current_user)

        question = await self.question_repository.get_obj_by_id(question_id)
        if not question or question.quiz_id != quiz.id:
            raise QuestionNotFoundException(question_id)

        remaining_questions = await self.question_repository.get_questions_for_quiz(question.quiz_id)
        if len(remaining_questions) <= 2:
            raise InvalidFieldException("A quiz must have at least 2 questions.")

        await self.question_repository.delete_obj(question_id)
        await self.quiz_repository.session.commit()


def get_quiz_service(
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> QuizService:
    return QuizService(
        quiz_repository=QuizRepository(session),
        question_repository=QuestionRepository(session),
        company_repository=CompanyRepository(session),
        membership_repository=CompanyMembershipRepository(session),
    )
