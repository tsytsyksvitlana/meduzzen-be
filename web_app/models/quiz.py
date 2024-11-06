from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web_app.models.base import Base


class Quiz(Base):
    """
    Model for storing information about quizzes within a company.
    """

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    participation_frequency: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Participation frequency in days"
    )
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("Company.id", ondelete="CASCADE"), nullable=False
    )
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
    company = relationship(
        "Company",
        back_populates="quizzes"
    )
    questions = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan"
    )
    participations = relationship(
        "QuizParticipation",
        back_populates="quiz"
    )

    def __repr__(self) -> str:
        return f"Quiz(id={self.id}, title={self.title}, company_id={self.company_id})"
