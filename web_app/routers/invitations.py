import logging

from fastapi import APIRouter, Depends, Query, status

from web_app.models import User
from web_app.schemas.company import CompanyInfoResponse
from web_app.schemas.invitation import (
    InvitationForCompanySchema,
    InvitationForUserSchema,
    InvitationRetrieveSchema,
    InvitationSendSchema,
    InvitationsListResponse
)
from web_app.schemas.user import UserSchema
from web_app.services.invitations.invitation_service import (
    InvitationService,
    get_invitation_service
)
from web_app.utils.auth import get_current_user

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post(
    "/company/{company_id}/send",
    response_model=InvitationRetrieveSchema,
    status_code=status.HTTP_201_CREATED
)
async def invite_member(
    company_id: int,
    invitation_data: InvitationSendSchema,
    current_user: User = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    """
    Allow owners to send invitations to users to join company.
    """
    invitation = await invitation_service.send_invitation(
        company_id=company_id,
        owner_id=current_user.id,
        user_id=invitation_data.user_id
    )
    return InvitationRetrieveSchema(
        company_id=invitation.company_id,
        user_id=invitation.user_id,
        status=invitation.status,
        sent_at=invitation.sent_at,
    )


@router.get(
    "/user/{user_id}",
    response_model=InvitationsListResponse,
    status_code=status.HTTP_200_OK
)
async def get_user_invitations(
    user_id: int,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    """
    Retrieves a list of invitations for a specific user with pagination.
    """
    invitations, total_count = await invitation_service.get_user_invitations(
        user_id, current_user.id, limit, offset
    )
    return InvitationsListResponse(
        invitations=[
            InvitationForUserSchema(
                id=inv.id,
                company=CompanyInfoResponse(
                    id=inv.company_id,
                    name=inv.company.name,
                    description=inv.company.description,
                    is_visible=inv.company.is_visible,
                    address=inv.company.address,
                    contact_email=inv.company.contact_email,
                    phone_number=inv.company.phone_number,
                ),
                status=inv.status,
                requested_at=inv.sent_at,
            ) for inv in invitations
        ],
        total_count=total_count
    )


@router.put(
    "/{invitation_id}/decline",
    status_code=status.HTTP_200_OK
)
async def decline_invitation(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    """
    Allows user to decline an invitation.
    """
    await invitation_service.decline_invitation(invitation_id, current_user.id)
    return {"message": "Invitation declined successfully"}


@router.post(
    "/{invitation_id}/accept",
    status_code=status.HTTP_200_OK
)
async def accept_invitation(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    """
    Allows user to accept an invitation.
    """
    await invitation_service.accept_invitation(invitation_id, current_user.id)
    return {"message": "Invitation accepted successfully"}


@router.put(
    "/{invitation_id}/cancel",
    status_code=status.HTTP_200_OK
)
async def cancel_invitation(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    """
    Allows owner to cancel send invitation.
    """
    await invitation_service.cancel_invitation(invitation_id, current_user.id)
    return {"message": "Invitation canceled successfully"}


@router.get(
    "/company/{company_id}",
    status_code=status.HTTP_200_OK,
)
async def view_invitations(
    company_id: int,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    """
    Retrieves a list of invitations sent by the company with pagination.
    """
    invitations, total_count = await invitation_service.get_company_invitations(
        company_id, current_user.id, limit, offset
    )
    return {
        "invitations": [
            InvitationForCompanySchema(
                id=inv.id,
                user=UserSchema(
                    id=inv.user_id,
                    firt_name=inv.user.first_name,
                    last_name=inv.user.last_name,
                    email=inv.user.email,
                    created_at=inv.sent_at,
                    updated_at=inv.user.updated_at,
                    last_activity_at=inv.user.last_activity_at,
                ),
                status=inv.status,
                requested_at=inv.sent_at,
            ) for inv in invitations
        ],
        "total_count": total_count,
    }
