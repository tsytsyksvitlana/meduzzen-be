from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from web_app.schemas.company import CompanyInfoResponse
from web_app.schemas.user import UserSchema


class InvitationStatus(Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    CANCELED = "Canceled"


class InvitationSendSchema(BaseModel):
    company_id: int
    user_id: int


class InvitationRetrieveSchema(BaseModel):
    company_id: int
    user_id: int
    status: str
    sent_at: datetime


class InvitationForCompanySchema(BaseModel):
    id: int
    user: UserSchema
    status: str
    requested_at: datetime


class InvitationForUserSchema(BaseModel):
    id: int
    company: CompanyInfoResponse
    status: str
    requested_at: datetime


class InvitationsListResponse(BaseModel):
    invitations: list[InvitationForUserSchema] | list[InvitationForCompanySchema]
    total_count: int
