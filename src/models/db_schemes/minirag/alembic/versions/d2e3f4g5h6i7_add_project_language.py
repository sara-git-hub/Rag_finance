"""add project language

Revision ID: d2e3f4g5h6i7
Revises: c7d8e9f0g1h2
Create Date: 2025-01-21 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd2e3f4g5h6i7'
down_revision: Union[str, Sequence[str], None] = 'c7d8e9f0g1h2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add project_language column to projects table."""
    # Add project_language column with default value 'fr'
    op.add_column('projects',
        sa.Column('project_language', sa.String(length=2), nullable=False, server_default='fr')
    )

    # Create index for faster lookups by language
    op.create_index('ix_project_language', 'projects', ['project_language'], unique=False)


def downgrade() -> None:
    """Downgrade schema - Remove project_language column."""
    op.drop_index('ix_project_language', table_name='projects')
    op.drop_column('projects', 'project_language')
