from fastapi import APIRouter, Depends, status

from web_app.models import User
from web_app.schemas.company import CompanyInfoResponse
from web_app.schemas.join_request import (
    JoinRequestForCompanySchema,
    JoinRequestForUserSchema
)
from web_app.schemas.user import UserSchema
from web_app.services.join_requests.join_request_service import (
    JoinRequestService,
    get_join_request_service
)
from web_app.utils.auth import get_current_user

router = APIRouter()


@router.post(
    "/company/{company_id}/join",
    status_code=status.HTTP_201_CREATED
)
async def request_join(
    company_id: int,
    current_user: User = Depends(get_current_user),
    join_request_service: JoinRequestService = Depends(get_join_request_service),
):
    """
    Send user's request to join a specific company.
    """
    join_request = await join_request_service.request_to_join(
        company_id, current_user.id
    )
    return {
        "message": "Join request sent successfully",
        "request_id": join_request.id
    }


@router.delete(
    "/join_request/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def cancel_join_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    join_request_service: JoinRequestService = Depends(get_join_request_service),
):
    """Cancels user's previously sent join request."""
    await join_request_service.cancel_request(request_id, current_user.id)


@router.post(
    "/join_request/{request_id}/accept",
    status_code=status.HTTP_200_OK
)
async def accept_join_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    join_request_service: JoinRequestService = Depends(get_join_request_service),
):
    """Allows company's owner to accept a join request from a user."""
    await join_request_service.accept_request(request_id, current_user.id)
    return {"message": "Join request accepted"}


@router.post(
    "/join_request/{request_id}/decline",
    status_code=status.HTTP_200_OK
)
async def decline_join_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    join_request_service: JoinRequestService = Depends(get_join_request_service),
):
    """Allows company's owner to decline a join request from a user."""
    await join_request_service.decline_request(request_id, current_user.id)
    return {"message": "Join request declined"}


@router.get(
    "/user/{user_id}/join_requests",
    response_model=list[JoinRequestForUserSchema],
    status_code=status.HTTP_200_OK
)
async def get_user_join_requests(
    user_id: int,
    current_user: User = Depends(get_current_user),
    join_request_service: JoinRequestService = Depends(get_join_request_service),
):
    """
    Retrieves all join requests made by a specified user.
    """
    requests = await join_request_service.get_user_requests(user_id, current_user.id)
    return [JoinRequestForUserSchema(
                id=req.id,
                company=CompanyInfoResponse(
                    id=req.company.id,
                    name=req.company.name,
                    description=req.company.description,
                    is_visible=req.company.is_visible,
                    address=req.company.address,
                    contact_email=req.company.contact_email,
                    phone_number=req.company.phone_number,
                ),
                status=req.status,
                requested_at=req.requested_at
            ) for req in requests]


@router.get(
    "/company/{company_id}/pending_requests",
    response_model=list[JoinRequestForCompanySchema],
    status_code=status.HTTP_200_OK
)
async def get_pending_requests(
    company_id: int,
    current_user: User = Depends(get_current_user),
    join_request_service: JoinRequestService = Depends(get_join_request_service),
):
    """
    Retrieves all pending membership requests for a specific company.
    Only accessible by the company's owner.
    """
    pending_requests = await join_request_service.get_pending_requests(company_id, current_user.id)
    return [JoinRequestForCompanySchema(
                id=req.id,
                user=UserSchema(
                    id=req.user.id,
                    first_name=req.user.first_name,
                    last_name=req.user.last_name,
                    email=req.user.email,
                    created_at=req.user.created_at,
                    updated_at=req.user.updated_at,
                    last_activity_at=req.user.last_activity_at,
                ),
                status=req.status,
                requested_at=req.requested_at
            ) for req in pending_requests]
