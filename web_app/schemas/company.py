from typing import List

from pydantic import BaseModel


class CompanyCreateSchema(BaseModel):
    name: str
    description: str
    is_visible: bool
    address: str
    contact_email: str = None
    phone_number: str = None


class OwnerSchema(BaseModel):
    first_name: str
    last_name: str


class CompanyDetailSchema(BaseModel):
    name: str
    description: str
    is_visible: bool
    address: str
    contact_email: str
    phone_number: str
    owner: OwnerSchema


class CompanyListResponse(BaseModel):
    list: List[CompanyDetailSchema]
    total_count: int
