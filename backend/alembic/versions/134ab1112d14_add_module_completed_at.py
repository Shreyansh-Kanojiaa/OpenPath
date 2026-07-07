"""add_module_completed_at

Revision ID: 134ab1112d14
Revises: 42f79984e882
Create Date: 2026-07-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '134ab1112d14'
down_revision: Union[str, Sequence[str], None] = '42f79984e882'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('modules', sa.Column('completed_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('modules', 'completed_at')
