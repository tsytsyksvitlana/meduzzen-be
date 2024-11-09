from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, StreamingResponse

from web_app.exceptions.validation import InvalidFieldException
from web_app.models import User
from web_app.services.quizzes.quiz_service import QuizService, get_quiz_service
from web_app.utils.auth import get_current_user
from web_app.utils.data_exporter import DataExporter

router = APIRouter()


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
