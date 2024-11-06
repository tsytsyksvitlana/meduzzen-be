from fastapi import APIRouter, Depends

from web_app.models import User
from web_app.schemas.quiz import QuizCreate
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
