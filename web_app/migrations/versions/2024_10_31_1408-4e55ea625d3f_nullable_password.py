"""nullable password

Revision ID: 4e55ea625d3f
Revises: 822686fc4e34
Create Date: 2024-10-31 14:08:59.684912

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4e55ea625d3f'
down_revision: Union[str, None] = '822686fc4e34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(),
               nullable=True)


def downgrade() -> None:
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(),
               nullable=False)
