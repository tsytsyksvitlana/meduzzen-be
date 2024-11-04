"""added join request

Revision ID: 1ea8211bbbe0
Revises: 13a41218226d
Create Date: 2024-11-04 19:54:27.812603

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1ea8211bbbe0'
down_revision: Union[str, None] = '13a41218226d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('JoinRequest',
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['Company.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_JoinRequest_status'), 'JoinRequest', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_JoinRequest_status'), table_name='JoinRequest')
    op.drop_table('JoinRequest')
