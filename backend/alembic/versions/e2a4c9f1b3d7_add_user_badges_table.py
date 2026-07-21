"""add_user_badges_table

Revision ID: e2a4c9f1b3d7
Revises: c7e9828ae968
Create Date: 2026-07-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2a4c9f1b3d7'
down_revision: Union[str, Sequence[str], None] = 'c7e9828ae968'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_badges',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), index=True),
        sa.Column('badge_key', sa.String(), index=True),
        sa.Column('earned_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('user_id', 'badge_key', name='uq_user_badge'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_badges')
