import json

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.config.constants import (
    MIN_QUESTION_ANSWER_COUNT,
    MIN_QUIZ_QUESTION_COUNT
)
from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.db.redis_helper import redis_helper
from web_app.exceptions.companies import CompanyNotFoundException
from web_app.exceptions.data import DataNotFoundException
from web_app.exceptions.permission import PermissionDeniedException
from web_app.exceptions.quizzes import (
    AnswerNotFoundException,
    QuestionNotFoundException,
    QuizNotFoundException
)
from web_app.exceptions.validation import InvalidFieldException
from web_app.models import Notification, QuizParticipation, User, UserAnswer
from web_app.models.answer import Answer
from web_app.models.question import Question
from web_app.models.quiz import Quiz
from web_app.repositories.answer_repository import AnswerRepository
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.repositories.notification_repository import NotificationRepository
from web_app.repositories.question_repository import QuestionRepository
from web_app.repositories.quiz_participation_repository import (
    QuizParticipationRepository
)
from web_app.repositories.quiz_repository import QuizRepository
from web_app.repositories.user_answer_repository import UserAnswerRepository
from web_app.schemas.quiz import (
    CompanyAverageScoreData,
    LastQuizParticipation,
    MonthlyQuizScore,
    QuestionCreate,
    QuizCreate,
    QuizParticipationSchema,
    QuizScoreTimeData,
    QuizUpdate,
    UserLastQuizAttempt,
    UserQuizDetailScoreData
)
from web_app.schemas.roles import Role
from web_app.schemas.user import OverallUserRating


class QuizService:
    def __init__(
        self,
        quiz_repository: QuizRepository,
        question_repository: QuestionRepository,
        answer_repository: AnswerRepository,
        user_answer_repository: UserAnswerRepository,
        quiz_participation_repository: QuizParticipationRepository,
        company_repository: CompanyRepository,
        membership_repository: CompanyMembershipRepository,
        notification_repository: NotificationRepository,
    ):
        self.quiz_repository = quiz_repository
        self.question_repository = question_repository
        self.answer_repository = answer_repository
        self.user_answer_repository = user_answer_repository
        self.quiz_participation_repository = quiz_participation_repository
        self.membership_repository = membership_repository
        self.company_repository = company_repository
        self.notification_repository = notification_repository

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

        users = await self.company_repository.get_users_for_company(quiz.company_id)

        for user in users:
            message = (
                "A new quiz has been created."
                "You are invited to participate!"
            )
            notification = Notification(user_id=user.id, message=message)
            await self.notification_repository.create_obj(notification)
            await self.notification_repository.session.flush()
        await self.notification_repository.session.commit()

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

    async def _get_user_scores_by_quiz(
            self, participations: list
    ) -> dict:
        scores_by_quiz = {}

        for participation in participations:
            quiz = participation.quiz
            if quiz:
                month_year = participation.participated_at.strftime("%Y-%m")
                score_percentage = participation.calculate_score_percentage()

                if quiz.id not in scores_by_quiz:
                    scores_by_quiz[quiz.id] = {}
                if month_year not in scores_by_quiz[quiz.id]:
                    scores_by_quiz[quiz.id][month_year] = []

                scores_by_quiz[quiz.id][month_year].append(score_percentage)

        return scores_by_quiz

    async def get_user_overall_rating(self, user_id: int):
        participations = await self.quiz_participation_repository.get_quizzes_by_user_id(user_id)
        if not participations:
            raise DataNotFoundException("User has no participations in quizzes.")

        total_score, total_questions = 0, 0
        for participation in participations:
            total_score += participation.score
            total_questions += participation.total_questions

        if total_questions == 0:
            raise DataNotFoundException("User have no questions in quizzes.")

        overall_rating = (total_score / total_questions)*100
        return OverallUserRating(
            user_id=user_id,
            overall_rating=overall_rating
        )

    async def get_user_quiz_scores_with_time(self, user_id: int) -> list[QuizScoreTimeData]:
        participations = await self.quiz_participation_repository.get_quizzes_by_user_id_with_quiz(user_id)
        if not participations:
            raise DataNotFoundException("User has no participations in quizzes.")

        scores_by_quiz = await self._get_user_scores_by_quiz(participations)

        quiz_scores_time_data = [
            QuizScoreTimeData(
                quiz_id=quiz_id,
                scores_by_month={
                    month_year: MonthlyQuizScore(scores=scores, average=sum(scores) / len(scores))
                    for month_year, scores in time_data.items()
                }
            )
            for quiz_id, time_data in scores_by_quiz.items()
        ]

        return quiz_scores_time_data

    async def get_user_last_quiz_participations(self, user_id: int) -> list[LastQuizParticipation]:
        participations = await self.quiz_participation_repository.get_quizzes_by_user_id_with_quiz(user_id)
        if not participations:
            raise DataNotFoundException("No quiz participations found for this user")

        last_participations = {}
        for participation in participations:
            quiz = participation.quiz
            if quiz:
                if (
                        quiz.id not in last_participations
                        or last_participations[quiz.id].last_participation_at < participation.participated_at
                ):
                    last_participations[quiz.id] = LastQuizParticipation(
                        quiz_id=quiz.id,
                        quiz_title=quiz.title,
                        last_participation_at=participation.participated_at,
                    )

        return list(last_participations.values())

    async def save_quiz_participation_to_redis(
        self,
        quiz_participation: QuizParticipation
    ):
        participation_data = {
            "user_id": quiz_participation.user_id,
            "company_id": quiz_participation.company_id,
            "quiz_id": quiz_participation.quiz_id,
            "total_questions": quiz_participation.total_questions,
            "correct_answers": quiz_participation.score,
            "score_percentage": quiz_participation.calculate_score_percentage(),
        }

        user_quiz_key = f"quiz:{quiz_participation.quiz_id}:user:{quiz_participation.id}"
        await redis_helper.set(user_quiz_key, json.dumps(participation_data))

        user_quizzes_key = f"user:{quiz_participation.user_id}:quizzes"
        await redis_helper.rpush(user_quizzes_key, json.dumps(participation_data))

        company_quiz_users_key = f"company:{quiz_participation.company_id}:quiz:{quiz_participation.quiz_id}:users"
        await redis_helper.rpush(company_quiz_users_key, json.dumps(participation_data))

        company_quizzes_key = f"company:{quiz_participation.company_id}:user:{quiz_participation.user_id}:quizzes"
        await redis_helper.sadd(company_quizzes_key, quiz_participation.quiz_id)

    async def user_quiz_participation(
        self,
        quiz_participation: QuizParticipationSchema,
        current_user: User
    ):
        user_answers = quiz_participation.user_answers
        quiz_id = quiz_participation.quiz_id
        quiz = await self.quiz_repository.get_obj_by_id(quiz_id)
        if not quiz:
            raise QuizNotFoundException(quiz_id)

        questions = await self.question_repository.get_questions_for_quiz(quiz.id)
        total_questions_count = len(questions)
        if total_questions_count < MIN_QUIZ_QUESTION_COUNT:
            raise InvalidFieldException("A quiz must have at least 2 questions.")

        participation_data = {
            "user_id": current_user.id,
            "company_id": quiz.company_id,
            "quiz_id": quiz_id,
            "question_answers": []
        }

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

                participation_data["question_answers"].append({
                    "question_id": question.id,
                    "user_answer_id": answer.id,
                    "is_correct": is_correct
                })

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
        await self.save_quiz_participation_to_redis(participation)

        return participation

    async def export_quiz_results_for_company(
            self, quiz_id: int, company_id: int, current_user: User
    ) -> list[dict]:
        await self.check_is_owner_or_admin(company_id, current_user)

        company_quiz_users_key = f"company:{company_id}:quiz:{quiz_id}:users"

        raw_participation_data = await redis_helper.lrange(company_quiz_users_key, 0, -1)
        if not raw_participation_data:
            raise DataNotFoundException()

        participation_data = [json.loads(entry) for entry in raw_participation_data]

        return participation_data

    async def export_quiz_results_for_user(
            self, quiz_id: int, user_id: int, current_user: User
    ) -> dict:
        if current_user.id != user_id:
            raise PermissionDeniedException()

        user_quiz_key = f"quiz:{quiz_id}:user:{user_id}"

        raw_participation_data = await redis_helper.get(user_quiz_key)

        if raw_participation_data:
            participation_data = json.loads(raw_participation_data)
        else:
            raise DataNotFoundException()

        return participation_data

    async def export_all_quiz_results_for_user(self, company_id: int, user_id: int, current_user: User):
        await self.check_is_owner_or_admin(company_id, current_user)

        user_quizzes_key = f"user:{user_id}:quizzes"
        raw_user_quizzes = await redis_helper.lrange(user_quizzes_key, 0, -1)
        if not raw_user_quizzes:
            raise DataNotFoundException()

        user_quizzes = [json.loads(entry) for entry in raw_user_quizzes]
        return user_quizzes

    async def export_all_quiz_results_for_company(
        self, company_id, quiz_id, user_id: int, current_user: User
    ):
        await self.check_is_owner_or_admin(company_id, current_user)

        user_quiz_key = f"company:{company_id}:user:{user_id}:quizzes"
        raw_quiz_result = await redis_helper.get(user_quiz_key)

        if raw_quiz_result:
            quiz_result = json.loads(raw_quiz_result)
        else:
            raise DataNotFoundException()
        return quiz_result

    async def get_company_average_scores_over_time(
            self, company_id: int, current_user: User
    ) -> list[CompanyAverageScoreData]:
        await self.check_is_owner_or_admin(company_id, current_user)
        participations = await self.quiz_participation_repository.get_company_participations(company_id)

        if not participations:
            raise DataNotFoundException("No quiz participations found for this company.")

        scores_over_time = {}

        for participation in participations:
            month_year = participation.participated_at.strftime("%Y-%m")
            score_percentage = participation.calculate_score_percentage()

            if month_year not in scores_over_time:
                scores_over_time[month_year] = []

            scores_over_time[month_year].append(score_percentage)

        company_scores_data = [
            CompanyAverageScoreData(
                time_period=month_year,
                average_score=(sum(scores) / len(scores))
            )
            for month_year, scores in scores_over_time.items()
        ]

        return company_scores_data

    async def get_user_detailed_quiz_scores_for_company(
            self, company_id: int, user_id: int, current_user: User
    ) -> list[UserQuizDetailScoreData]:
        await self.check_is_owner_or_admin(company_id, current_user)
        participations = await self.quiz_participation_repository.get_company_quizzes_by_user_id_with_quiz(
            user_id, company_id
        )

        if not participations:
            raise DataNotFoundException("No quiz participations found for this user in company.")

        user_scores = await self._get_user_scores_by_quiz(participations)

        detailed_scores = [
            UserQuizDetailScoreData(
                quiz_id=quiz_id,
                scores_by_month={
                    month_year: sum(scores) / len(scores)
                    for month_year, scores in time_data.items()
                }
            )
            for quiz_id, time_data in user_scores.items()
        ]
        return detailed_scores

    async def get_company_users_last_quiz_attempts(
            self, company_id: int, current_user: User
    ) -> list[UserLastQuizAttempt]:
        await self.check_is_owner_or_admin(company_id, current_user)
        participations = await self.quiz_participation_repository.get_company_participations(company_id)
        if not participations:
            raise DataNotFoundException("No quiz participations found for this company.")

        last_quiz_attempts = {}
        for participation in participations:
            user = participation.user
            if (
                    user.id not in last_quiz_attempts
                    or last_quiz_attempts[user.id].last_attempt_at < participation.participated_at
            ):
                last_quiz_attempts[user.id] = UserLastQuizAttempt(
                    user_id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    last_attempt_at=participation.participated_at,
                )
        return list(last_quiz_attempts.values())


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
        notification_repository=NotificationRepository(session),
    )
