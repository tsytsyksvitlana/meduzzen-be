from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web_app.models.base import Base


class Question(Base):
    """
    Model for storing questions within a quiz.
    """
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    quiz_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("Quiz.id", ondelete="CASCADE"), nullable=False
    )

    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Question(id={self.id}, title={self.title}, quiz_id={self.quiz_id})"
