import io
import logging

import pandas as pd
from fastapi import Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.exceptions.application import (
    ApplicationErrorException,
    BadRequestException
)
from web_app.exceptions.validation import InvalidFieldException
from web_app.models import User
from web_app.repositories.answer_repository import AnswerRepository
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.repositories.notification_repository import NotificationRepository
from web_app.repositories.question_repository import QuestionRepository
from web_app.repositories.quiz_repository import QuizRepository
from web_app.schemas.quiz import (
    AnswerCreate,
    QuestionCreate,
    QuizCreate,
    QuizUpdate
)
from web_app.services.quizzes.quiz_service import QuizService

logger = logging.getLogger(__name__)


class ImportService(QuizService):
    def __init__(
        self,
        membership_repository: CompanyMembershipRepository,
        quiz_repository: QuizRepository,
        question_repository: QuestionRepository,
        answer_repository: AnswerRepository,
        company_repository: CompanyRepository,
        notification_repository: NotificationRepository,
    ):
        super().__init__(
            quiz_repository=quiz_repository,
            question_repository=question_repository,
            answer_repository=answer_repository,
            user_answer_repository=None,
            quiz_participation_repository=None,
            company_repository=company_repository,
            membership_repository=membership_repository,
            notification_repository=notification_repository,
        )
        self.membership_repository = membership_repository
        self.quiz_repository = quiz_repository
        self.question_repository = question_repository
        self.answer_repository = answer_repository

    async def import_quizzes(self, file: UploadFile, current_user: User):
        if (
            file.content_type
            != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            raise BadRequestException(
                "Invalid file type. Please upload an Excel file.",
            )

        try:
            content = await file.read()
            excel_data = pd.ExcelFile(io.BytesIO(content))

            quizzes_df = excel_data.parse("quizzes").fillna(
                {"title": "", "description": "", "participation_frequency": 0}
            )
            questions_df = excel_data.parse("questions").fillna({"title": ""})
            answers_df = excel_data.parse("answers").fillna(
                {"text": "", "is_correct": False}
            )

            for _, quiz_row in quizzes_df.iterrows():
                await self._import_or_update_quiz(
                    quiz_row, questions_df, answers_df, current_user
                )

            await self._import_or_update_questions(questions_df, answers_df)

            return {"detail": "Import successful."}
        except Exception as e:
            raise ApplicationErrorException(f"Error processing file: {str(e)}")

    async def _import_or_update_quiz(
        self, quiz_row, questions_df, answers_df, current_user
    ):
        quiz = await self.quiz_repository.get_obj_by_id(quiz_row["quiz_id"])

        title = quiz_row["title"] if pd.notna(quiz_row["title"]) else (quiz.title if quiz else None)
        description = (
            quiz_row["description"]
            if pd.notna(quiz_row["description"])
            else (quiz.description if quiz else None)
        )
        participation_frequency = (
            int(quiz_row["participation_frequency"])
            if pd.notna(quiz_row["participation_frequency"])
            else (quiz.participation_frequency if quiz else None)
        )
        company_id = int(quiz_row["company_id"])

        quiz_data = {
            "title": title,
            "description": description,
            "participation_frequency": participation_frequency,
            "company_id": company_id,
        }

        if quiz is None:
            required_fields = ["title", "description", "participation_frequency"]
            if not all(quiz_data.get(field) for field in required_fields):
                raise InvalidFieldException(
                    f"Missing required fields for creating quiz {quiz_row['quiz_id']}."
                )

            quiz_create = QuizCreate(
                **quiz_data,
                questions=self._parse_questions(
                    questions_df, answers_df, quiz_row["quiz_id"]
                ),
            )
            return await self.create_quiz(quiz_create, current_user=current_user)

        quiz_update = QuizUpdate(
            title=quiz_data["title"],
            description=quiz_data["description"],
            participation_frequency=quiz_data["participation_frequency"],
        )
        return await self.update_quiz(
            quiz.id, quiz_update, current_user=current_user
        )

    async def _import_or_update_questions(self, questions_df, answers_df):
        questions = []
        for _, question_row in questions_df.iterrows():
            questions.append(await self._process_question_and_answers(question_row, answers_df))
        return questions

    async def _parse_questions(self, questions_df, answers_df, quiz_id):
        questions = []
        relevant_questions = questions_df[questions_df["quiz_id"] == quiz_id]
        for _, question_row in relevant_questions.iterrows():
            questions.append(await self._process_question_and_answers(question_row, answers_df))
        return questions

    async def _process_question_and_answers(self, question_row, answers_df):
        question_id = question_row["question_id"]
        question = await self.question_repository.get_obj_by_id(question_id)

        title = question_row["title"]
        if question:
            if title and question.title != title:
                question.title = title
                await self.question_repository.update_obj(question)
                await self.question_repository.session.commit()
                await self.question_repository.session.refresh(question)

        answers = [
            AnswerCreate(
                text=answer_row["text"],
                is_correct=answer_row["is_correct"],
            )
            for _, answer_row in answers_df[answers_df["question_id"] == question_id].iterrows()
        ]

        return QuestionCreate(id=question_id, title=title, answers=answers)


def get_import_service(
    session: AsyncSession = Depends(pg_helper.session_getter),
) -> ImportService:
    return ImportService(
        membership_repository=CompanyMembershipRepository(session),
        quiz_repository=QuizRepository(session),
        question_repository=QuestionRepository(session),
        answer_repository=AnswerRepository(session),
        company_repository=CompanyRepository(session),
        notification_repository=NotificationRepository(session),
    )
