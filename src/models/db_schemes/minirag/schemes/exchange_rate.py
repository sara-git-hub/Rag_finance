"""
Exchange Rate Schema
Stockage des taux de change MAD/EUR et MAD/USD
"""

from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, Float, Date, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Index
import uuid
import enum


class CurrencyPair(str, enum.Enum):
    """Paires de devises supportées"""
    MAD_EUR = "MAD/EUR"
    MAD_USD = "MAD/USD"


class RateType(str, enum.Enum):
    """Type de taux (réel vs prédit)"""
    ACTUAL = "actual"      # Taux réel récupéré de BAM
    PREDICTED = "predicted"  # Taux prédit par le modèle


class ExchangeRate(SQLAlchemyBase):
    """
    Table pour stocker les taux de change quotidiens
    """
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rate_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    # Identification
    currency_pair = Column(SQLEnum(CurrencyPair, name='currencypair', values_callable=lambda x: [e.value for e in x]), nullable=False)
    date = Column(Date, nullable=False)  # Date du taux
    rate_type = Column(SQLEnum(RateType, name='ratetype', values_callable=lambda x: [e.value for e in x]), nullable=False, default=RateType.ACTUAL)

    # Taux de change
    achat = Column(Float, nullable=False)  # Taux d'achat (cours acheteur)
    vente = Column(Float, nullable=False)  # Taux de vente (cours vendeur)
    moyenne = Column(Float, nullable=True)  # Moyenne des deux (optionnel)

    # Métadonnées
    source = Column(String, nullable=True)  # Source des données (ex: "BAM API", "LSTM Model")
    confidence_score = Column(Float, nullable=True)  # Score de confiance pour prédictions (0-1)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Index pour performances
    __table_args__ = (
        Index('ix_exchange_rate_currency_date', currency_pair, date),
        Index('ix_exchange_rate_date', date),
        Index('ix_exchange_rate_type', rate_type),
        # Contrainte d'unicité : une seule entrée par (paire, date, type)
        Index('uq_exchange_rate', currency_pair, date, rate_type, unique=True)
    )


class ModelMetrics(SQLAlchemyBase):
    """
    Table pour stocker les métriques des modèles ML
    """
    __tablename__ = "exchange_rate_model_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identification du modèle
    model_version = Column(String, nullable=False)  # ex: "lstm_v1.0"
    currency_pair = Column(SQLEnum(CurrencyPair, name='currencypair', values_callable=lambda x: [e.value for e in x]), nullable=False)

    # Métriques de performance
    mae = Column(Float, nullable=True)  # Mean Absolute Error
    mse = Column(Float, nullable=True)  # Mean Squared Error
    rmse = Column(Float, nullable=True)  # Root Mean Squared Error
    mape = Column(Float, nullable=True)  # Mean Absolute Percentage Error
    r2 = Column(Float, nullable=True)  # R² (Coefficient of Determination)

    # Période d'entraînement
    training_start_date = Column(Date, nullable=True)
    training_end_date = Column(Date, nullable=True)
    training_samples = Column(Integer, nullable=True)

    # Timestamps
    trained_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Index
    __table_args__ = (
        Index('ix_model_metrics_version', model_version),
        Index('ix_model_metrics_currency', currency_pair),
    )
