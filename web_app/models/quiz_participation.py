from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web_app.models.base import Base


class QuizParticipation(Base):
    """
    Model for storing user participation in quizzes.
    """
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False
    )
    quiz_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("Quiz.id", ondelete="CASCADE"), nullable=False
    )
    participated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )
    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("Company.id", ondelete="CASCADE"),
        nullable=False,
    )
    score: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=True, default=0)

    user = relationship("User", back_populates="quiz_participations")
    quiz = relationship("Quiz", back_populates="participations")
    company = relationship("Company", back_populates="participations")

    def calculate_score_percentage(self) -> float:
        if self.total_questions > 0:
            return (self.score / self.total_questions) * 100
        return 0

    def __repr__(self) -> str:
        return (f"QuizParticipation("
                f"user_id={self.user_id}, quiz_id={self.quiz_id}, "
                f"participated_at={self.participated_at})")
