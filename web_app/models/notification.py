import typing as t
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web_app.models.base import Base

NotificationStatus = t.Literal["Unread", "Read"]


class Notification(Base):
    """
    Model for storing notifications to inform users.
    """
    message: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        String, default="Unread", nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=False)

    user = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        """
        Provide a string representation of this notification.
        """
        return (
            f"Notification(message={self.message}, "
            f"timestamp={self.timestamp}, status={self.status})"
        )
