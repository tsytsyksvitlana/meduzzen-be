import typing as t
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web_app.models.base import Base

RequestStatus = t.Literal["Pending", "Accepted", "Canceled"]


class JoinRequest(Base):
    """
    Model for managing user requests to join a company.
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
    status: Mapped[RequestStatus] = mapped_column(
        String, index=True, nullable=False, default="Pending"
    )
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )

    user = relationship("User", back_populates="join_requests")
    company = relationship("Company", back_populates="join_requests")

    def __repr__(self) -> str:
        return (
            f"JoinRequest(company_id={self.company_id}, user_id={self.user_id}, "
            f"status={self.status}, requested_at={self.requested_at})"
        )
