"""participation relations

Revision ID: 1617d7501646
Revises: a01fc925787a
Create Date: 2024-11-07 12:50:31.237341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1617d7501646'
down_revision: Union[str, None] = 'a01fc925787a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('UserAnswer',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('answer_id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('is_correct', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['answer_id'], ['Answer.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['question_id'], ['Question.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('QuizParticipation', sa.Column('company_id', sa.Integer(), nullable=False))
    op.add_column('QuizParticipation', sa.Column('score', sa.Integer(), nullable=True))
    op.add_column('QuizParticipation', sa.Column('total_questions', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'QuizParticipation', 'Company', ['company_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint(None, 'QuizParticipation', type_='foreignkey')
    op.drop_column('QuizParticipation', 'total_questions')
    op.drop_column('QuizParticipation', 'score')
    op.drop_column('QuizParticipation', 'company_id')
    op.drop_table('UserAnswer')
