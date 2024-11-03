from fastapi import APIRouter, Depends, HTTPException

from web_app.models import User
from web_app.schemas.company import CompanyCreateSchema
from web_app.services.companies.company_service import (
    CompanyService,
    get_company_service
)
from web_app.utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=CompanyCreateSchema)
async def create_company(
    company_data: CompanyCreateSchema,
    current_user: User = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service)
):
    try:
        new_company = await company_service.create_company(current_user, company_data)
        return new_company
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
