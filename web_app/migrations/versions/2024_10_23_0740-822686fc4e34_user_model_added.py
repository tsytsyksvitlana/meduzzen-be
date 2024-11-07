"""user model added

Revision ID: 822686fc4e34
Revises:
Create Date: 2024-10-23 07:40:35.397510

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "822686fc4e34"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "User",
        sa.Column("first_name", sa.String(length=50), nullable=True),
        sa.Column("last_name", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "last_activity_at", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_User_email"), "User", ["email"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_User_email"), table_name="User")
    op.drop_table("User")
