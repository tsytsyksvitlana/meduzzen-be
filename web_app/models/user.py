from datetime import datetime, timezone

from sqlalchemy import DateTime, String, event
from sqlalchemy.orm import Mapped, mapped_column

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

    @staticmethod
    def update_timestamp(mapper, connection, target):
        """
        Updates the updated_at timestamp before the User object
        is updated in the database.
        """
        target.updated_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        """
        Provides a string representation of the User object, showing the email.
        """
        return f"User(id = {self.id}, email={self.email})"


event.listen(User, "before_update", User.update_timestamp)
