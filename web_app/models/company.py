from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web_app.models.base import Base


class Company(Base):
    """
    Model for storing information about a company.
    """
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    is_visable: Mapped[bool] = mapped_column(Boolean, nullable=False)
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

    members = relationship("CompanyMembership", back_populates="company")

    @staticmethod
    def update_timestamp(mapper, connection, target):
        """
        Updates the updated_at timestamp before the Company Object
        is updated in the database.
        """
        target.updated_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        """
        Provides a string representation of the Company including id and name.
        """
        return f"Company(id={self.id}, name={self.name})"


event.listen(Company, "before_update", Company.update_timestamp)
