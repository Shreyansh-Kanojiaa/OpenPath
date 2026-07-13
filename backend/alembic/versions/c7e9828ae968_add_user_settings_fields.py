"""add_user_settings_fields

Revision ID: c7e9828ae968
Revises: a1b2c3d4e5f6
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7e9828ae968'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('last_username_change_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('known_skills', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'known_skills')
    op.drop_column('users', 'last_username_change_at')
