from fastapi import APIRouter, Depends, status

from web_app.models import User
from web_app.schemas.quiz import (
    QuestionCreate,
    QuizCreate,
    QuizParticipationResult,
    QuizParticipationSchema,
    QuizUpdate
)
from web_app.services.quizzes.quiz_service import QuizService, get_quiz_service
from web_app.utils.auth import get_current_user

router = APIRouter()


@router.post("", response_model=QuizCreate)
async def create_quiz(
    quiz_data: QuizCreate,
    current_user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    created_quiz = await quiz_service.create_quiz(quiz_data, current_user)
    return created_quiz


@router.put("/{quiz_id}")
async def update_quiz(
    quiz_id: int,
    quiz_data: QuizUpdate,
    current_user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    updated_quiz = await quiz_service.update_quiz(
        quiz_id, quiz_data, current_user
    )
    return updated_quiz


@router.post("/{quiz_id}/questions", response_model=QuestionCreate)
async def add_question(
    quiz_id: int,
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    question = await quiz_service.add_question_to_quiz(
        quiz_id, question_data, current_user
    )
    return question


@router.delete(
    "/{quiz_id}/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_question(
    quiz_id: int,
    question_id: int,
    current_user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    await quiz_service.delete_question_from_quiz(
        quiz_id, question_id, current_user
    )


@router.get("/{company_id}")
async def get_quizzes(
    company_id: int,
    skip: int = 0,
    limit: int = 10,
    quiz_service: QuizService = Depends(get_quiz_service)
):
    quizzes = await quiz_service.get_quizzes_for_company(
        company_id=company_id, skip=skip, limit=limit
    )
    return quizzes


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    await quiz_service.delete_quiz(quiz_id, current_user)


@router.post("/participate")
async def create_quiz_participate(
    quiz_participation: QuizParticipationSchema,
    current_user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    participation = await quiz_service.user_quiz_participation(
        quiz_participation, current_user
    )
    participation_schema = QuizParticipationResult(
        quiz_id=participation.quiz_id,
        total_questions=participation.total_questions,
        correct_answers=participation.correct_answers,
        score_percentage=participation.calculate_score_percentage(),
    )
    return participation_schema
