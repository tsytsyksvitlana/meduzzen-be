from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, StreamingResponse

from web_app.exceptions.validation import InvalidFieldException
from web_app.models import User
from web_app.schemas.quiz import LastQuizParticipation, QuizScoreTimeData
from web_app.schemas.user import OverallUserRating
from web_app.services.quizzes.quiz_service import QuizService, get_quiz_service
from web_app.utils.auth import get_current_user
from web_app.utils.data_exporter import DataExporter

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
    quiz_service: QuizService = Depends(get_quiz_service),
):
    """
    Endpoint to get the user's last participation date for each quiz.
    """
    last_participations = await quiz_service.get_user_last_quiz_participations(user_id)
    return last_participations


async def generate_export_response(data, file_name: str, export_format: str):
    """
    Helper function to handle exporting data in JSON or CSV format.
    """
    if export_format == "json":
        temp_file_path = DataExporter.export_to_json(data, f"{file_name}.json")
        return FileResponse(
            temp_file_path,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={file_name}.json"}
        )
    elif export_format == "csv":
        csv_data = DataExporter.export_to_csv(data, f"{file_name}.csv")
        return StreamingResponse(
            csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={file_name}.csv"}
        )
    else:
        raise InvalidFieldException("Invalid format specified. Choose 'json' or 'csv'.")


@router.get("/company/{company_id}/quiz/{quiz_id}/export")
async def export_quiz_results_for_company(
    company_id: int,
    quiz_id: int,
    export_format: str,
    current_user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """
    Export quiz results for a company in either JSON or CSV format.
    """
    data = await quiz_service.export_quiz_results_for_company(
        quiz_id, company_id, current_user
    )
    file_name = f"quiz_{quiz_id}_company_{company_id}_results"
    return await generate_export_response(data, file_name, export_format)


@router.get("/user/{user_id}/quiz/{quiz_id}/export")
async def export_user_quiz_results(
    user_id: int,
    quiz_id: int,
    export_format: str,
    current_user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """
    Export the quiz results for a specific user in either JSON or CSV format.
    """
    data = await quiz_service.export_quiz_results_for_user(
        quiz_id, user_id, current_user
    )
    file_name = f"quiz_{quiz_id}_user_{user_id}_results"
    return await generate_export_response(data, file_name, export_format)


@router.get("/company/{company_id}/user/{user_id}/quizzes/export")
async def export_user_quizzes_results(
        company_id: int,
        user_id: int,
        export_format: str,
        current_user: User = Depends(get_current_user),
        quiz_service: QuizService = Depends(get_quiz_service)
):
    """
    Export all quizzes for a specific user within a company in either JSON or CSV format.
    """
    user_quizzes = await quiz_service.export_all_quiz_results_for_user(
        company_id, user_id, current_user
    )

    file_name = f"user_{user_id}_company_{company_id}_all_quizzes"
    return await generate_export_response(user_quizzes, file_name, export_format)


@router.get("/company/{company_id}/user/{user_id}/quiz/{quiz_id}/export")
async def get_specific_quiz_result_for_user_in_company(
        company_id: int,
        user_id: int,
        quiz_id: int,
        export_format: str,
        current_user: User = Depends(get_current_user),
        quiz_service: QuizService = Depends(get_quiz_service)
):
    """
    Export the specific quiz result for a user in a company in either JSON or CSV format.
    """
    quiz_result = await quiz_service.export_all_quiz_results_for_company(
        company_id, quiz_id, user_id, current_user
    )

    file_name = f"quiz_{quiz_id}_user_{user_id}_company_{company_id}_result"
    return await generate_export_response([quiz_result], file_name, export_format)
