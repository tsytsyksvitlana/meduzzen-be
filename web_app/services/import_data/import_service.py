import io

import pandas as pd
from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.models import User
from web_app.repositories.answer_repository import AnswerRepository
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.repositories.company_repository import CompanyRepository
from web_app.repositories.notification_repository import NotificationRepository
from web_app.repositories.question_repository import QuestionRepository
from web_app.repositories.quiz_repository import QuizRepository
from web_app.schemas.quiz import AnswerCreate, QuestionCreate, QuizCreate
from web_app.services.quizzes.quiz_service import QuizService


class ImportService(QuizService):
    def __init__(
        self,
        membership_repository: CompanyMembershipRepository,
        quiz_repository: QuizRepository,
        question_repository: QuestionRepository,
        answer_repository: AnswerRepository,
        company_repository: CompanyRepository,
        notification_repository: NotificationRepository
    ):
        super().__init__(
            quiz_repository=quiz_repository,
            question_repository=question_repository,
            answer_repository=answer_repository,
            user_answer_repository=None,
            quiz_participation_repository=None,
            company_repository=company_repository,
            membership_repository=membership_repository,
            notification_repository=notification_repository
        )
        self.membership_repository = membership_repository
        self.quiz_repository = quiz_repository
        self.question_repository = question_repository
        self.answer_repository = answer_repository

    async def import_quizzes(self, file: UploadFile, current_user: User):
        if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file.")

        try:
            content = await file.read()
            excel_data = pd.ExcelFile(io.BytesIO(content))

            quizzes_df = excel_data.parse("quizzes")
            questions_df = excel_data.parse("questions")
            answers_df = excel_data.parse("answers")

            for _, quiz_row in quizzes_df.iterrows():
                quiz = await self._import_or_update_quiz(quiz_row, questions_df, answers_df, current_user)
                print(f"Processed quiz: {quiz.title}")

            return {"detail": "Import successful."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    async def _import_or_update_quiz(self, quiz_row, questions_df, answers_df, current_user):
        quiz_create = QuizCreate(
            title=quiz_row["title"],
            description=quiz_row["description"],
            participation_frequency=int(quiz_row["participation_frequency"]),
            company_id=int(quiz_row["company_id"]),
            questions=self._parse_questions(questions_df, answers_df, quiz_row["quiz_id"]),
        )

        quiz = await self.quiz_repository.get_obj_by_id(quiz_row["quiz_id"])
        if not quiz:
            return await self.create_quiz(quiz_create, current_user=current_user)
        else:
            return await self.update_quiz(quiz.id, quiz_create, current_user=current_user)

    def _parse_questions(self, questions_df, answers_df, quiz_id):
        questions = []
        for _, question_row in questions_df[questions_df["quiz_id"] == quiz_id].iterrows():
            answers = [
                AnswerCreate(text=answer_row["text"], is_correct=answer_row["is_correct"])
                for _, answer_row in answers_df[answers_df["question_id"] == question_row["question_id"]].iterrows()
            ]
            question = QuestionCreate(
                id=question_row["question_id"],
                title=question_row["title"],
                answers=answers
            )
            questions.append(question)
        return questions


def get_import_service(session: AsyncSession = Depends(pg_helper.session_getter)) -> ImportService:
    return ImportService(
        membership_repository=CompanyMembershipRepository(session),
        quiz_repository=QuizRepository(session),
        question_repository=QuestionRepository(session),
        answer_repository=AnswerRepository(session),
        company_repository=CompanyRepository(session),
        notification_repository=NotificationRepository(session)
    )
