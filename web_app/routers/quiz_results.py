from fastapi import APIRouter, Depends

from web_app.models import User
from web_app.services.export.export_service import (
    ExportService,
    get_export_service
)
from web_app.utils.auth import get_current_user

router = APIRouter()


@router.get("/company/{company_id}/quiz/{quiz_id}/export")
async def export_quiz_results_for_company(
    company_id: int,
    quiz_id: int,
    export_format: str,
    current_user: User = Depends(get_current_user),
    quiz_export_service: ExportService = Depends(get_export_service)
):
    """
    Export quiz results for a company in either JSON or CSV format.
    """
    return await quiz_export_service.export_quiz_results_for_company(
        quiz_id, company_id, current_user, export_format
    )


@router.get("/user/{user_id}/quiz/{quiz_id}/export")
async def export_user_quiz_results(
    user_id: int,
    quiz_id: int,
    export_format: str,
    current_user: User = Depends(get_current_user),
    quiz_export_service: ExportService = Depends(get_export_service)
):
    """
    Export the quiz results for a specific user in either JSON or CSV format.
    """
    return await quiz_export_service.export_quiz_results_for_user(
        quiz_id, user_id, current_user, export_format
    )


@router.get("/company/{company_id}/user/{user_id}/quizzes/export")
async def export_user_quizzes_results(
    company_id: int,
    user_id: int,
    export_format: str,
    current_user: User = Depends(get_current_user),
    quiz_export_service: ExportService = Depends(get_export_service)
):
    """
    Export all quizzes for a specific user within a company in either JSON or CSV format.
    """
    return await quiz_export_service.export_all_quiz_results_for_user(
        company_id, user_id, current_user, export_format
    )


@router.get("/company/{company_id}/user/{user_id}/quiz/{quiz_id}/export")
async def get_specific_quiz_result_for_user_in_company(
    company_id: int,
    user_id: int,
    quiz_id: int,
    export_format: str,
    current_user: User = Depends(get_current_user),
    quiz_export_service: ExportService = Depends(get_export_service)
):
    """
    Export the specific quiz result for a user in a company in either JSON or CSV format.
    """
    return await quiz_export_service.export_all_quiz_results_for_company(
        company_id, quiz_id, user_id, current_user, export_format
    )
