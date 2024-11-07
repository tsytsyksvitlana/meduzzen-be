import logging

from fastapi import APIRouter, Depends, Query, status

from web_app.models import User
from web_app.schemas.company import (
    CompanyCreateSchema,
    CompanyDetailSchema,
    CompanyInfoResponse,
    CompanyListResponse,
    CompanyUpdateSchema,
    OwnerSchema
)
from web_app.schemas.user import UserSchema, UsersListResponse
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
    company = await company_service.get_company_with_members(company_id)

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
            first_name=company.owner.first_name,
            last_name=company.owner.last_name,
        )
    )
    return company_schema


@router.get("/", response_model=CompanyListResponse)
async def list_companies(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    company_service: CompanyService = Depends(get_company_service),
):
    companies, total_count = await company_service.get_companies_with_owners(
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
                first_name=company.owner.first_name,
                last_name=company.owner.last_name,
            ) if company.owner else None
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


@router.get("/{company_id}/users", response_model=UsersListResponse)
async def get_users_in_company(
    company_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    company_service: CompanyService = Depends(get_company_service),
):
    users, total_count = await company_service.get_users_in_company(company_id, limit, offset)
    user_schemas = [
        UserSchema(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_activity_at=user.last_activity_at
        ) for user in users
    ]
    return UsersListResponse(users=user_schemas, total_count=total_count)


@router.patch("/{company_id}/appoint_admin/{user_id}/")
async def appoint_admin(
    company_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
):
    await company_service.appoint_admin(company_id, user_id, current_user)
    logger.info(f"User with ID {user_id} appointed as admin in company {company_id}.")
    return {"msg": f"User {user_id} has been appointed as admin."}


@router.patch("/{company_id}/remove_admin/{user_id}/")
async def remove_admin(
    company_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
):
    await company_service.remove_admin(company_id, user_id, current_user)
    logger.info(f"User with ID {user_id} removed from admin role in company {company_id}.")
    return {"msg": f"User {user_id} has been removed from admin role."}


@router.get("/{company_id}/admins", response_model=UsersListResponse)
async def get_admins_in_company(
    company_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    company_service: CompanyService = Depends(get_company_service),
):
    admins, total_count = await company_service.get_admins_in_company(company_id, limit, offset)
    admin_schemas = [
        UserSchema(
            id=admin.id,
            first_name=admin.first_name,
            last_name=admin.last_name,
            email=admin.email,
            created_at=admin.created_at,
            updated_at=admin.updated_at,
            last_activity_at=admin.last_activity_at
        ) for admin in admins
    ]
    return UsersListResponse(users=admin_schemas, total_count=total_count)
