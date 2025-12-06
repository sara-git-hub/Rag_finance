"""add_project_name

Revision ID: f7a1975380af
Revises: e8f9g0h1i2j3
Create Date: 2025-12-06 21:25:42.778884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7a1975380af'
down_revision: Union[str, Sequence[str], None] = 'e8f9g0h1i2j3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('projects', sa.Column('project_name', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('projects', 'project_name')
