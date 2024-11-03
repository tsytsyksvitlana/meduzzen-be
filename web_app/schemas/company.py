from pydantic import BaseModel


class CompanyCreateSchema(BaseModel):
    name: str
    description: str
    is_visible: bool
    address: str
    contact_email: str = None
    phone_number: str = None
