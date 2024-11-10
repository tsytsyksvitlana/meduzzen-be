"""notification

Revision ID: 73a0a8887079
Revises: 1617d7501646
Create Date: 2024-11-10 18:40:50.410692

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '73a0a8887079'
down_revision: str | None = '1617d7501646'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('Notification',
    sa.Column('message', sa.String(length=200), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('Notification')
