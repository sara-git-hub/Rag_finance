"""add conversations and messages tables

Revision ID: c7d8e9f0g1h2
Revises: a1b2c3d4e5f6
Create Date: 2025-11-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c7d8e9f0g1h2'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add conversations and messages tables."""
    connection = op.get_bind()

    # Create enum type for conversation status
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'conversationstatus')"
    ))
    enum_exists = result.scalar()

    if not enum_exists:
        conversation_status_enum = postgresql.ENUM('active', 'archived', name='conversationstatus', create_type=False)
        conversation_status_enum.create(connection)

    conversation_status_enum = postgresql.ENUM('active', 'archived', name='conversationstatus', create_type=False)

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('conversation_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('conversation_uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('status', conversation_status_enum, nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('conversation_id'),
        sa.UniqueConstraint('conversation_uuid')
    )

    # Create indexes for conversations
    op.create_index('ix_conversations_conversation_id', 'conversations', ['conversation_id'], unique=False)
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'], unique=False)
    op.create_index('ix_conversations_project_id', 'conversations', ['project_id'], unique=False)

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('message_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.conversation_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('message_id')
    )

    # Create indexes for messages
    op.create_index('ix_messages_message_id', 'messages', ['message_id'], unique=False)
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema: Remove conversations and messages tables."""

    # Drop indexes for messages
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_index('ix_messages_message_id', table_name='messages')

    # Drop messages table
    op.drop_table('messages')

    # Drop indexes for conversations
    op.drop_index('ix_conversations_project_id', table_name='conversations')
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_index('ix_conversations_conversation_id', table_name='conversations')

    # Drop conversations table
    op.drop_table('conversations')

    # Drop enum type
    conversation_status_enum = postgresql.ENUM('active', 'archived', name='conversationstatus')
    conversation_status_enum.drop(op.get_bind(), checkfirst=True)
