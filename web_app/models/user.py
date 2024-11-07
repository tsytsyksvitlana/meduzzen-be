from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web_app.models.base import Base


class User(Base):
    """
    Model for storing a user.
    """

    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=True)
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
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    companies_membership = relationship(
        "CompanyMembership", back_populates="user"
    )
    invitations_received = relationship(
        "Invitation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    join_requests = relationship(
        "JoinRequest",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    quiz_participations = relationship(
        "QuizParticipation", back_populates="user", cascade="all, delete-orphan"
    )
    user_answers = relationship("UserAnswer", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """
        Provides a string representation of the User object, showing the email.
        """
        return f"User(id = {self.id}, email={self.email})"
