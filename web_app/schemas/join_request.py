from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from web_app.schemas.company import CompanyInfoResponse
from web_app.schemas.user import UserSchema


class JoinRequestStatus(Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    CANCELED = "Canceled"


class JoinRequestForCompanySchema(BaseModel):
    id: int
    user: UserSchema
    status: str
    requested_at: datetime


class JoinRequestForUserSchema(BaseModel):
    id: int
    company: CompanyInfoResponse
    status: str
    requested_at: datetime
