from fastapi import APIRouter, Depends, status

from web_app.models import User
from web_app.schemas.join_request import JoinRequestRetrieveSchema
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
    join_request = await join_request_service.request_to_join(company_id, current_user.id)
    return {"message": "Join request sent successfully", "request_id": join_request.id}


@router.delete(
    "/join_request/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def cancel_join_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    join_request_service: JoinRequestService = Depends(get_join_request_service),
):
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
    await join_request_service.decline_request(request_id, current_user.id)
    return {"message": "Join request declined"}


@router.get(
    "/user/{user_id}/join_requests",
    response_model=list[JoinRequestRetrieveSchema],
    status_code=status.HTTP_200_OK
)
async def get_user_join_requests(
    user_id: int,
    current_user: User = Depends(get_current_user),
    join_request_service: JoinRequestService = Depends(get_join_request_service),
):
    requests = await join_request_service.get_user_requests(current_user.id)
    return requests
