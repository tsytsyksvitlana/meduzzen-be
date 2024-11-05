from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.join_request import JoinRequest
from web_app.repositories.base_repository import BaseRepository


class JoinRequestRepository(BaseRepository[JoinRequest]):
    def __init__(self, session: AsyncSession):
        super().__init__(JoinRequest, session)

    async def get_request(self, company_id: int, user_id: int) -> JoinRequest | None:
        query = (
            select(JoinRequest)
            .where(
                JoinRequest.company_id == company_id,
                JoinRequest.user_id == user_id
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_user_requests(self, user_id: int) -> list[JoinRequest]:
        query = (
            select(JoinRequest)
            .where(JoinRequest.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
