import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from web_app.models import User
from web_app.schemas.company import (
    CompanyCreateSchema,
    CompanyDetailSchema,
    OwnerSchema, CompanyListResponse
)
from web_app.services.companies.company_service import (
    CompanyService,
    get_company_service
)
from web_app.utils.auth import get_current_user

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/{company_id}/", response_model=CompanyDetailSchema)
async def get_company(
        company_id: int,
        company_service: CompanyService = Depends(get_company_service),
):
    company = await company_service.get_company(company_id)

    owner_membership = next(
        (membership for membership in company.members
         if membership.role == "Owner"), None
    )

    if not owner_membership or not owner_membership.user:
        raise HTTPException(
            status_code=404,
            detail="Owner not found for this company."
        )

    logger.info(f"Fetched company with ID {company_id} successfully.")

    company_schema = CompanyDetailSchema(
        name=company.name,
        description=company.description,
        is_visible=company.is_visible,
        address=company.address,
        contact_email=company.contact_email,
        phone_number=company.phone_number,
        owner=OwnerSchema(
            first_name=owner_membership.user.first_name,
            last_name=owner_membership.user.last_name,
        )
    )
    return company_schema


@router.get("/", response_model=CompanyListResponse)
async def list_companies(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    company_service: CompanyService = Depends(get_company_service),
):
    companies, total_count = await company_service.get_companies(
        limit=limit, offset=offset
    )
    company_schemas = [
        CompanyDetailSchema(
            name=company.name,
            description=company.description,
            is_visible=company.is_visible,
            address=company.address,
            contact_email=company.contact_email,
            phone_number=company.phone_number,
            owner=OwnerSchema(
                first_name=membership.user.first_name,
                last_name=membership.user.last_name,
            ) if (membership := next(
                (m for m in company.members if m.role == "Owner"), None
            )) else None,
        )
        for company in companies
    ]
    return CompanyListResponse(list=company_schemas, total_count=total_count)


@router.post("/", response_model=CompanyCreateSchema)
async def create_company(
    company_data: CompanyCreateSchema,
    current_user: User = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
):
    try:
        new_company = await company_service.create_company(current_user, company_data)
        return new_company
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
