from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web_app.models.base import Base


class Answer(Base):
    """
    Model for storing answers for a question.
    """
    text: Mapped[str] = mapped_column(String(200), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("Question.id", ondelete="CASCADE"), nullable=False
    )

    question = relationship("Question", back_populates="answers")
    user_answers = relationship("UserAnswer", back_populates="answer")

    def __repr__(self) -> str:
        return (f"Answer("
                f"id={self.id}, text={self.text}, "
                f"is_correct={self.is_correct}, question_id={self.question_id})")
