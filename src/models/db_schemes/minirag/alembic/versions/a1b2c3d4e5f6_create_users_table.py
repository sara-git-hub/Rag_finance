"""create users table

Revision ID: a1b2c3d4e5f6
Revises: 5f7aed4b55b1
Create Date: 2025-01-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '5f7aed4b55b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum type for user roles if it doesn't exist
    connection = op.get_bind()

    # Check if the enum type already exists using raw SQL
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole')"
    ))
    enum_exists = result.scalar()

    # Only create the enum if it doesn't exist
    if not enum_exists:
        user_role_enum = postgresql.ENUM('admin', 'user', name='userrole', create_type=False)
        user_role_enum.create(connection)

    # Use the enum type (whether newly created or already existing)
    user_role_enum = postgresql.ENUM('admin', 'user', name='userrole', create_type=False)

    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', user_role_enum, nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('user_uuid'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

    # Create indexes
    op.create_index('ix_users_username', 'users', ['username'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')

    # Drop table
    op.drop_table('users')

    # Drop enum type
    user_role_enum = postgresql.ENUM('admin', 'user', name='userrole')
    user_role_enum.drop(op.get_bind(), checkfirst=True)
