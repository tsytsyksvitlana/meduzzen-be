"""added company and companymembership

Revision ID: 70099d8a4801
Revises: 4e55ea625d3f
Create Date: 2024-11-04 15:52:48.317258

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '70099d8a4801'
down_revision: str | None = '4e55ea625d3f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('Company',
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=False),
    sa.Column('is_visible', sa.Boolean(), nullable=False),
    sa.Column('address', sa.String(length=100), nullable=True),
    sa.Column('contact_email', sa.String(length=100), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('CompanyMembership',
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['Company.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_CompanyMembership_role'), 'CompanyMembership', ['role'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_CompanyMembership_role'), table_name='CompanyMembership')
    op.drop_table('CompanyMembership')
    op.drop_table('Company')
