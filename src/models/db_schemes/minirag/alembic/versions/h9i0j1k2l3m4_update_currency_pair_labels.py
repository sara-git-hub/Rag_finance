"""update currency pair labels from MAD/EUR to EUR/MAD

Revision ID: h9i0j1k2l3m4
Revises: g8h9i0j1k2l3
Create Date: 2025-01-29 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'h9i0j1k2l3m4'
down_revision = 'g8h9i0j1k2l3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Modifier l'ENUM currencypair : MAD/EUR → EUR/MAD, MAD/USD → USD/MAD
    Les valeurs numériques restent inchangées (1 EUR = X MAD)

    Note: Les valeurs ENUM EUR/MAD et USD/MAD doivent déjà exister dans la DB
    """
    # Mettre à jour les données existantes (juste changer les étiquettes)
    op.execute("""
        UPDATE exchange_rates
        SET currency_pair = 'EUR/MAD'
        WHERE currency_pair = 'MAD/EUR'
    """)

    op.execute("""
        UPDATE exchange_rates
        SET currency_pair = 'USD/MAD'
        WHERE currency_pair = 'MAD/USD'
    """)

    op.execute("""
        UPDATE exchange_rate_model_metrics
        SET currency_pair = 'EUR/MAD'
        WHERE currency_pair = 'MAD/EUR'
    """)

    op.execute("""
        UPDATE exchange_rate_model_metrics
        SET currency_pair = 'USD/MAD'
        WHERE currency_pair = 'MAD/USD'
    """)


def downgrade() -> None:
    """
    Revenir à MAD/EUR et MAD/USD
    """
    connection = op.get_bind()

    # Revenir aux anciennes étiquettes
    connection.execute(sa.text("""
        UPDATE exchange_rates
        SET currency_pair = 'MAD/EUR'
        WHERE currency_pair = 'EUR/MAD';
    """))

    connection.execute(sa.text("""
        UPDATE exchange_rates
        SET currency_pair = 'MAD/USD'
        WHERE currency_pair = 'USD/MAD';
    """))

    connection.execute(sa.text("""
        UPDATE exchange_rate_model_metrics
        SET currency_pair = 'MAD/EUR'
        WHERE currency_pair = 'EUR/MAD';
    """))

    connection.execute(sa.text("""
        UPDATE exchange_rate_model_metrics
        SET currency_pair = 'MAD/USD'
        WHERE currency_pair = 'USD/MAD';
    """))
