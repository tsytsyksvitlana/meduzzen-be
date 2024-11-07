from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.config.constants import (
    MIN_QUESTION_ANSWER_COUNT,
    MIN_QUIZ_QUESTION_COUNT
)
from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.exceptions.companies import CompanyNotFoundException
from web_app.exceptions.permission import PermissionDeniedException
from web_app.exceptions.quizzes import (
    AnswerNotFoundException,
    QuestionNotFoundException,
    QuizNotFoundException
)
from web_app.exceptions.validation import InvalidFieldException
from web_app.models import QuizParticipation, User, UserAnswer
from web_app.models.answer import Answer
from web_app.models.question import Question
from web_app.models.quiz import Quiz
from web_app.repositories.answer_repository import AnswerRepository
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.repositories.question_repository import QuestionRepository
from web_app.repositories.quiz_participation_repository import (
    QuizParticipationRepository
)
from web_app.repositories.quiz_repository import QuizRepository
from web_app.repositories.user_answer_repository import UserAnswerRepository
from web_app.schemas.quiz import (
    QuestionCreate,
    QuizCreate,
    QuizParticipationSchema,
    QuizUpdate
)
from web_app.schemas.roles import Role


class QuizService:
    def __init__(
        self,
        quiz_repository: QuizRepository,
        question_repository: QuestionRepository,
        answer_repository: AnswerRepository,
        user_answer_repository: UserAnswerRepository,
        quiz_participation_repository: QuizParticipationRepository,
        company_repository: CompanyRepository,
        membership_repository: CompanyMembershipRepository
    ):
        self.quiz_repository = quiz_repository
        self.question_repository = question_repository
        self.answer_repository = answer_repository
        self.user_answer_repository = user_answer_repository
        self.quiz_participation_repository = quiz_participation_repository
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
        if not quiz_data.questions or len(quiz_data.questions) < MIN_QUIZ_QUESTION_COUNT:
            raise InvalidFieldException(
                "The quiz must have at least two questions."
            )

        for question_data in quiz_data.questions:
            if len(question_data.answers) < MIN_QUESTION_ANSWER_COUNT:
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

        if len(question_data.answers) < MIN_QUESTION_ANSWER_COUNT:
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
        if len(remaining_questions) <= MIN_QUIZ_QUESTION_COUNT:
            raise InvalidFieldException("A quiz must have at least 2 questions.")

        await self.question_repository.delete_obj(question_id)
        await self.quiz_repository.session.commit()

    async def user_quiz_participation(self, quiz_participation: QuizParticipationSchema, current_user: User):
        user_answers = quiz_participation.user_answers
        quiz_id = quiz_participation.quiz_id
        quiz = await self.quiz_repository.get_obj_by_id(quiz_id)
        if not quiz:
            raise QuizNotFoundException(quiz_id)

        questions = await self.question_repository.get_questions_for_quiz(quiz.id)
        total_questions_count = len(questions)
        if total_questions_count < MIN_QUIZ_QUESTION_COUNT:
            raise InvalidFieldException("A quiz must have at least 2 questions.")

        correct_answers_count = 0
        for user_answer in user_answers:
            question = await self.question_repository.get_obj_by_id(user_answer.question_id)
            if not question:
                raise QuestionNotFoundException(user_answer.question_id)
            answer = await self.answer_repository.get_obj_by_id(user_answer.answer_id)
            if not answer:
                raise AnswerNotFoundException(user_answer.question_id)
            if is_correct := answer.is_correct:
                correct_answers_count += 1
                user_answer_obj = UserAnswer(
                    user_id=current_user.id,
                    answer_id=user_answer.answer_id,
                    question_id=question.id,
                    is_correct=is_correct
                )
                await self.user_answer_repository.create_obj(user_answer_obj)

        participation = QuizParticipation(
            quiz_id=quiz_id,
            user_id=current_user.id,
            company_id=quiz.company_id,
            score=correct_answers_count,
            total_questions=total_questions_count,
        )
        await self.quiz_participation_repository.create_obj(participation)
        await self.quiz_participation_repository.session.commit()
        return participation


def get_quiz_service(
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> QuizService:
    return QuizService(
        quiz_repository=QuizRepository(session),
        question_repository=QuestionRepository(session),
        answer_repository=AnswerRepository(session),
        user_answer_repository=UserAnswerRepository(session),
        quiz_participation_repository=QuizParticipationRepository(session),
        company_repository=CompanyRepository(session),
        membership_repository=CompanyMembershipRepository(session),
    )
