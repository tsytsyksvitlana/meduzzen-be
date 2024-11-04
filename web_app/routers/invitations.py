from fastapi import APIRouter, Depends, Query, status

from web_app.models import User
from web_app.schemas.invitation import (
    InvitationRetrieveSchema,
    InvitationSendSchema,
    InvitationsListResponse
)
from web_app.services.invitations.invitation_service import (
    InvitationService,
    get_invitation_service
)
from web_app.utils.auth import get_current_user

router = APIRouter()

@router.post(
    "/{company_id}/invite",
    response_model=InvitationRetrieveSchema,
    status_code=status.HTTP_201_CREATED
)
async def invite_member(
    company_id: int,
    invitation_data: InvitationSendSchema,
    current_user: User = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
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
    "/invitations",
    response_model=InvitationsListResponse,
    status_code=status.HTTP_200_OK
)
async def get_user_invitations(
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    invitations, total_count = await invitation_service.get_user_invitations(current_user.id, limit, offset)
    return InvitationsListResponse(
        invitations=[
            InvitationRetrieveSchema(
                company_id=inv.company_id,
                user_id=inv.user_id,
                status=inv.status,
                sent_at=inv.sent_at,
            ) for inv in invitations
        ],
        total_count=total_count
    )
