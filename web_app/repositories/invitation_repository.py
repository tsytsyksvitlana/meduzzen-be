from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.models.invitation import Invitation
from web_app.repositories.base_repository import BaseRepository


class InvitationRepository(BaseRepository[Invitation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Invitation, session)

    async def get_invitation(self, company_id: int, user_id: int) -> Invitation | None:
        query = (
            select(Invitation)
            .where(
                Invitation.company_id == company_id,
                Invitation.user_id == user_id
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_user_invitations(self, user_id: int, limit: int, offset: int) -> list[Invitation]:
        query = (
            select(Invitation)
            .where(Invitation.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_total_invitations_count(self, user_id: int) -> int:
        query = select(func.count()).where(Invitation.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar()
