from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web_app.models.base import Base


class UserAnswer(Base):
    """
    Model for storing user's answers for a question during a quiz.
    """
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("User.id", ondelete="CASCADE"),
        nullable=False
    )
    answer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("Answer.id", ondelete="CASCADE"),
        nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("Question.id", ondelete="CASCADE"),
        nullable=False
    )
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)

    user = relationship("User", back_populates="user_answers")
    answer = relationship("Answer", back_populates="user_answers")
    question = relationship("Question", back_populates="user_answers")

    def __repr__(self) -> str:
        return f"UserAnswer(user_id={self.user_id}, answer_id={self.answer_id}, is_correct={self.is_correct})"
