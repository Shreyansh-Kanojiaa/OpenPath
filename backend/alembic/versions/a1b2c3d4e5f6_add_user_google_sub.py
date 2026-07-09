"""add_user_google_sub

Revision ID: a1b2c3d4e5f6
Revises: 134ab1112d14
Create Date: 2026-07-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '134ab1112d14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('google_sub', sa.String(), nullable=True))
    op.create_index('ix_users_google_sub', 'users', ['google_sub'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_users_google_sub', table_name='users')
    op.drop_column('users', 'google_sub')
