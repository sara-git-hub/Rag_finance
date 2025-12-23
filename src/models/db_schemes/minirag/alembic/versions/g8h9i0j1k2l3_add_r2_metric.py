"""add_r2_metric

Revision ID: g8h9i0j1k2l3
Revises: f7a1975380af
Create Date: 2025-12-22 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g8h9i0j1k2l3'
down_revision: Union[str, Sequence[str], None] = 'f7a1975380af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('exchange_rate_model_metrics', sa.Column('r2', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('exchange_rate_model_metrics', 'r2')
