from fastapi import APIRouter, Depends

from web_app.models import User
from web_app.schemas.quiz import (
    CompanyAverageScoreData,
    LastQuizParticipation,
    QuizScoreTimeData,
    UserLastQuizAttempt,
    UserQuizDetailScoreData
)
from web_app.schemas.user import OverallUserRating
from web_app.services.quizzes.quiz_service import QuizService, get_quiz_service
from web_app.utils.auth import get_current_user

router = APIRouter()


@router.get("/user/{user_id}/overall_rating", response_model=OverallUserRating)
async def get_user_overall_rating(
    user_id: int,
    quiz_service: QuizService = Depends(get_quiz_service),
):
    """
    Retrieve the overall rating (average score) for a specific user across all quizzes.
    """
    user_rating = await quiz_service.get_user_overall_rating(user_id)
    return user_rating


@router.get("/user/{user_id}/quiz_scores_with_time", response_model=list[QuizScoreTimeData])
async def get_quiz_scores_with_time(
    user_id: int,
    quiz_service: QuizService = Depends(get_quiz_service),
):
    """
    Endpoint to get user's average scores for each quiz over time, grouped by month.
    """
    quiz_scores = await quiz_service.get_user_quiz_scores_with_time(user_id)
    return quiz_scores


@router.get(
    "/user/{user_id}/last_quiz_participations",
    response_model=list[LastQuizParticipation]
)
async def get_user_last_quiz_participations(
    user_id: int,
    current_user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    """
    Endpoint to get the user's last participation date for each quiz.
    """
    last_participations = await quiz_service.get_user_last_quiz_participations(
        user_id, current_user
    )
    return last_participations


@router.get(
    "/company/{company_id}/average_scores_over_time",
    response_model=list[CompanyAverageScoreData]
)
async def get_company_average_scores_over_time(
    company_id: int,
    current_user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """
    Get average scores of all company members over time (monthly).
    """
    average_scores = await quiz_service.get_company_average_scores_over_time(
        company_id, current_user
    )
    return average_scores


@router.get(
    "/company/{company_id}/user/{user_id}/detailed_quiz_scores",
    response_model=list[UserQuizDetailScoreData]
)
async def get_user_detailed_quiz_scores(
    company_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """
    Get average scores for each quiz taken by a user over time (monthly).
    """
    detailed_scores = await quiz_service.get_user_detailed_quiz_scores_for_company(
        company_id, user_id, current_user
    )
    return detailed_scores


@router.get(
    "/company/{company_id}/users_last_attempts",
    response_model=list[UserLastQuizAttempt]
)
async def get_company_users_last_quiz_attempts(
    company_id: int,
    current_user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """
    Get a list of all users in a company with their last quiz attempt timestamp.
    """
    last_attempts = await quiz_service.get_company_users_last_quiz_attempts(
        company_id, current_user
    )
    return last_attempts
