import typing as t
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web_app.models.base import Base

Role = t.Literal["Admin", "Owner", "Member"]


class CompanyMembership(Base):
    """
    Model for storing membership records of users within a company.
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
    role: Mapped[Role] = mapped_column(
        String, index=True, nullable=False, default="Member"
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="companies_membership")
    company = relationship("Company", back_populates="members")

    def __repr__(self) -> str:
        return (
            f"CompanyMembership(company_id={self.company_id}, "
            f"user_id={self.user_id}, role={self.role})"
        )
