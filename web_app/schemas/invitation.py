from datetime import datetime
from enum import Enum

from pydantic import BaseModel


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


class InvitationsListResponse(BaseModel):
    invitations: list[InvitationRetrieveSchema]
    total_count: int
