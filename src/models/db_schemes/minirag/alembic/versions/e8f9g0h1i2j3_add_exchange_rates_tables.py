"""add exchange rates tables

Revision ID: e8f9g0h1i2j3
Revises: d2e3f4g5h6i7
Create Date: 2025-01-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e8f9g0h1i2j3'
down_revision = 'd2e3f4g5h6i7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Créer les types enum s'ils n'existent pas déjà en utilisant SQL brut
    connection = op.get_bind()
    connection.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE currencypair AS ENUM ('MAD/EUR', 'MAD/USD');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))

    connection.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE ratetype AS ENUM ('actual', 'predicted');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))

    # Créer la table exchange_rates
    op.create_table(
        'exchange_rates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('rate_uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('currency_pair', postgresql.ENUM('MAD/EUR', 'MAD/USD', name='currencypair', create_type=False), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('rate_type', postgresql.ENUM('actual', 'predicted', name='ratetype', create_type=False), nullable=False),
        sa.Column('achat', sa.Float(), nullable=False),
        sa.Column('vente', sa.Float(), nullable=False),
        sa.Column('moyenne', sa.Float(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rate_uuid')
    )

    # Créer les index
    op.create_index('ix_exchange_rate_currency_date', 'exchange_rates', ['currency_pair', 'date'])
    op.create_index('ix_exchange_rate_date', 'exchange_rates', ['date'])
    op.create_index('ix_exchange_rate_type', 'exchange_rates', ['rate_type'])
    op.create_index('uq_exchange_rate', 'exchange_rates', ['currency_pair', 'date', 'rate_type'], unique=True)

    # Créer la table model_metrics
    op.create_table(
        'exchange_rate_model_metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('model_version', sa.String(), nullable=False),
        sa.Column('currency_pair', postgresql.ENUM('MAD/EUR', 'MAD/USD', name='currencypair', create_type=False), nullable=False),
        sa.Column('mae', sa.Float(), nullable=True),
        sa.Column('mse', sa.Float(), nullable=True),
        sa.Column('rmse', sa.Float(), nullable=True),
        sa.Column('mape', sa.Float(), nullable=True),
        sa.Column('training_start_date', sa.Date(), nullable=True),
        sa.Column('training_end_date', sa.Date(), nullable=True),
        sa.Column('training_samples', sa.Integer(), nullable=True),
        sa.Column('trained_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Créer les index pour model_metrics
    op.create_index('ix_model_metrics_version', 'exchange_rate_model_metrics', ['model_version'])
    op.create_index('ix_model_metrics_currency', 'exchange_rate_model_metrics', ['currency_pair'])


def downgrade() -> None:
    # Supprimer les index
    op.drop_index('ix_model_metrics_currency', table_name='exchange_rate_model_metrics')
    op.drop_index('ix_model_metrics_version', table_name='exchange_rate_model_metrics')
    op.drop_index('uq_exchange_rate', table_name='exchange_rates')
    op.drop_index('ix_exchange_rate_type', table_name='exchange_rates')
    op.drop_index('ix_exchange_rate_date', table_name='exchange_rates')
    op.drop_index('ix_exchange_rate_currency_date', table_name='exchange_rates')

    # Supprimer les tables
    op.drop_table('exchange_rate_model_metrics')
    op.drop_table('exchange_rates')

    # Supprimer les types enum
    sa.Enum(name='ratetype').drop(op.get_bind())
    sa.Enum(name='currencypair').drop(op.get_bind())
