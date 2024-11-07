import typing as t
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web_app.models.base import Base

InvitationStatus = t.Literal["Pending", "Accepted", "Canceled"]


class Invitation(Base):
    """
    Model for managing invitations sent by an owner to other users to join a company.
    """

    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("Company.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("User.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[InvitationStatus] = mapped_column(
        String, index=True, nullable=False, default="Pending"
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="invitations_received")
    company = relationship("Company", back_populates="invitations")

    def __repr__(self) -> str:
        return (
            f"Invitation(company_id={self.company_id}, user_id={self.user_id}, "
            f"status={self.status}, sent_at={self.sent_at})"
        )
