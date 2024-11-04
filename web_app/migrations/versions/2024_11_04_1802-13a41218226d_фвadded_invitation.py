"""фвadded invitation

Revision ID: 13a41218226d
Revises: 70099d8a4801
Create Date: 2024-11-04 18:02:27.022020

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '13a41218226d'
down_revision: Union[str, None] = '70099d8a4801'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('Invitation',
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['Company.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Invitation_status'), 'Invitation', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_Invitation_status'), table_name='Invitation')
    op.drop_table('Invitation')
