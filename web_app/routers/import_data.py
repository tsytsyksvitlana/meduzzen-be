from fastapi import APIRouter, Depends, UploadFile

from web_app.models import User
from web_app.services.import_data.import_service import (
    ImportService,
    get_import_service
)
from web_app.utils.auth import get_current_user

router = APIRouter()


@router.post("/import-quizzes")
async def import_quizzes(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    import_service: ImportService = Depends(get_import_service),
):
    """
    Import quizzes from Excel file.
    """
    return await import_service.import_quizzes(file, current_user)
