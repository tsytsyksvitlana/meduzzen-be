from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.join_request import JoinRequest
from web_app.repositories.base_repository import BaseRepository


class JoinRequestRepository(BaseRepository[JoinRequest]):
    def __init__(self, session: AsyncSession):
        super().__init__(JoinRequest, session)
