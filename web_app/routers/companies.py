import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from web_app.models import User
from web_app.schemas.company import (
    CompanyCreateSchema,
    CompanyDetailSchema,
    CompanyInfoResponse,
    CompanyListResponse,
    CompanyUpdateSchema,
    OwnerSchema
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
        id=company.id,
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
            id=company.id,
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
    new_company = await company_service.create_company(current_user, company_data)
    if new_company is None:
        logger.error("An error occurred while creating company.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    logger.info(f"Created company with ID {new_company.id} successfully.")
    return new_company


@router.patch("/toggle_visibility/{company_id}/")
async def toggle_visibility(
    company_id: int,
    current_user: User = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
):
    company = await company_service.toggle_visibility(
        company_id=company_id, current_user=current_user
    )
    logger.info(f"Company with ID {company_id} changed is_visible to {company.is_visible}")
    return {"msg": "Visibility changed successfully."}


@router.delete("/{company_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
) -> None:
    await company_service.delete_company(company_id, current_user)
    logger.info(f"Deleted company with ID {company_id}.")


@router.put("/{company_id}", response_model=CompanyInfoResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdateSchema,
    current_user: User = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
):
    company = await company_service.update_company(
        company_id, company_data, current_user
    )
    logger.info(f"Updated company with ID {company_id}.")
    company_schema = CompanyInfoResponse(
        id=company.id,
        name=company.name,
        description=company.description,
        is_visible=company.is_visible,
        address=company.address,
        contact_email=company.contact_email,
        phone_number=company.phone_number,
    )
    return company_schema
