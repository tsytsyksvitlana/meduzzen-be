from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web_app.models.base import Base


class Company(Base):
    """
    Model for storing information about a company.
    """
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False)
    address: Mapped[str] = mapped_column(String(100), nullable=True)
    contact_email: Mapped[str] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    members = relationship(
        "CompanyMembership",
        back_populates="company",
        cascade="all, delete-orphan"
    )
    invitations = relationship(
        "Invitation",
        back_populates="company",
        cascade="all, delete-orphan"
    )
    join_requests = relationship(
        "JoinRequest",
        back_populates="company",
        cascade="all, delete-orphan"
    )
    quizzes = relationship(
        "Quiz",
        back_populates="company",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """
        Provides a string representation of the Company including id and name.
        """
        return f"Company(id={self.id}, name={self.name})"
