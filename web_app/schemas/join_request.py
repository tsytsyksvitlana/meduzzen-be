from datetime import datetime

from pydantic import BaseModel


class JoinRequestRetrieveSchema(BaseModel):
    id: int
    company_id: int
    user_id: int
    status: str
    requested_at: datetime

    class Config:
        orm_mode = True
