"""
Exchange Rate Model
Gestion des opérations de base de données pour les taux de change
"""

import logging
from typing import List, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy import and_, desc
from models.db_schemes import ExchangeRate, ModelMetrics, CurrencyPair, RateType
from exchange_rates.metrics import EXCHANGE_RATES_IN_DB

logger = logging.getLogger(__name__)


class ExchangeRateModel:
    """Modèle pour gérer les taux de change"""

    def __init__(self, db_client):
        """
        Initialize Exchange Rate Model

        Args:
            db_client: Database client (async context manager)
        """
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client):
        """Create an instance of ExchangeRateModel"""
        return cls(db_client=db_client)

    async def insert_rate(
        self,
        currency_pair: CurrencyPair,
        date: date,
        achat: float,
        vente: float,
        rate_type: RateType = RateType.ACTUAL,
        source: Optional[str] = None,
        confidence_score: Optional[float] = None
    ) -> ExchangeRate:
        """
        Insérer un nouveau taux de change

        Args:
            currency_pair: Paire de devises (EUR/MAD ou USD/MAD)
            date: Date du taux
            achat: Taux d'achat
            vente: Taux de vente
            rate_type: Type de taux (actual ou predicted)
            source: Source des données
            confidence_score: Score de confiance pour prédictions

        Returns:
            ExchangeRate créé
        """
        async with self.db_client() as session:
            async with session.begin():
                # Calculer la moyenne
                moyenne = (achat + vente) / 2

                rate = ExchangeRate(
                    currency_pair=currency_pair,
                    date=date,
                    rate_type=rate_type,
                    achat=achat,
                    vente=vente,
                    moyenne=moyenne,
                    source=source,
                    confidence_score=confidence_score
                )

                session.add(rate)
                await session.flush()
                await session.refresh(rate)

                EXCHANGE_RATES_IN_DB.labels(
                    currency_pair=currency_pair.value,
                    rate_type=rate_type.value
                ).inc()

            return rate

    async def insert_rates_batch(self, rates: List[dict]) -> int:
        """
        Insérer plusieurs taux de change en une seule transaction

        Args:
            rates: Liste de dictionnaires contenant les données de taux

        Returns:
            Nombre de taux insérés
        """
        async with self.db_client() as session:
            async with session.begin():
                rate_objects = []
                for rate_data in rates:
                    moyenne = (rate_data['achat'] + rate_data['vente']) / 2

                    rate = ExchangeRate(
                        currency_pair=rate_data['currency_pair'],
                        date=rate_data['date'],
                        rate_type=rate_data.get('rate_type', RateType.ACTUAL),
                        achat=rate_data['achat'],
                        vente=rate_data['vente'],
                        moyenne=moyenne,
                        source=rate_data.get('source'),
                        confidence_score=rate_data.get('confidence_score')
                    )
                    rate_objects.append(rate)

                session.add_all(rate_objects)

                for rate_data in rates:
                    EXCHANGE_RATES_IN_DB.labels(
                        currency_pair=rate_data['currency_pair'].value,
                        rate_type=rate_data.get('rate_type', RateType.ACTUAL).value
                    ).inc()

            return len(rate_objects)

    async def get_rates_by_date_range(
        self,
        currency_pair: CurrencyPair,
        start_date: date,
        end_date: date,
        rate_type: Optional[RateType] = None
    ) -> List[ExchangeRate]:
        """
        Récupérer les taux de change sur une période

        Args:
            currency_pair: Paire de devises
            start_date: Date de début
            end_date: Date de fin
            rate_type: Type de taux (None = tous)

        Returns:
            Liste des taux de change
        """
        async with self.db_client() as session:
            query = select(ExchangeRate).where(
                and_(
                    ExchangeRate.currency_pair == currency_pair,
                    ExchangeRate.date >= start_date,
                    ExchangeRate.date <= end_date
                )
            )

            if rate_type:
                query = query.where(ExchangeRate.rate_type == rate_type)

            query = query.order_by(ExchangeRate.date.asc())

            result = await session.execute(query)
            return result.scalars().all()

    async def get_latest_rate(
        self,
        currency_pair: CurrencyPair,
        rate_type: RateType = RateType.ACTUAL
    ) -> Optional[ExchangeRate]:
        """
        Récupérer le dernier taux de change disponible

        Args:
            currency_pair: Paire de devises
            rate_type: Type de taux

        Returns:
            Dernier taux de change ou None
        """
        async with self.db_client() as session:
            query = select(ExchangeRate).where(
                and_(
                    ExchangeRate.currency_pair == currency_pair,
                    ExchangeRate.rate_type == rate_type
                )
            ).order_by(desc(ExchangeRate.date)).limit(1)

            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_historical_data(
        self,
        currency_pair: CurrencyPair,
        days: int = 365,
        rate_type: RateType = RateType.ACTUAL
    ) -> List[ExchangeRate]:
        """
        Récupérer l'historique des N derniers jours

        Args:
            currency_pair: Paire de devises
            days: Nombre de jours d'historique
            rate_type: Type de taux

        Returns:
            Liste des taux de change
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        return await self.get_rates_by_date_range(
            currency_pair=currency_pair,
            start_date=start_date,
            end_date=end_date,
            rate_type=rate_type
        )

    async def rate_exists(
        self,
        currency_pair: CurrencyPair,
        date: date,
        rate_type: RateType = RateType.ACTUAL
    ) -> bool:
        """
        Vérifier si un taux existe déjà pour une date donnée

        Args:
            currency_pair: Paire de devises
            date: Date à vérifier
            rate_type: Type de taux

        Returns:
            True si le taux existe
        """
        async with self.db_client() as session:
            query = select(ExchangeRate).where(
                and_(
                    ExchangeRate.currency_pair == currency_pair,
                    ExchangeRate.date == date,
                    ExchangeRate.rate_type == rate_type
                )
            )

            result = await session.execute(query)
            return result.scalar_one_or_none() is not None

    async def delete_predictions(
        self,
        currency_pair: CurrencyPair,
        start_date: Optional[date] = None
    ) -> int:
        """
        Supprimer les prédictions (pour ré-entraîner le modèle)

        Args:
            currency_pair: Paire de devises
            start_date: Date de début (None = toutes les prédictions)

        Returns:
            Nombre de prédictions supprimées
        """
        from sqlalchemy import delete as sql_delete

        logger.info(f"delete_predictions called: currency_pair={currency_pair}, start_date={start_date}")

        async with self.db_client() as session:
            async with session.begin():
                query = sql_delete(ExchangeRate).where(
                    and_(
                        ExchangeRate.currency_pair == currency_pair,
                        ExchangeRate.rate_type == RateType.PREDICTED
                    )
                )

                if start_date:
                    query = query.where(ExchangeRate.date >= start_date)
                    logger.info(f"Deleting predictions from {start_date} onwards")
                else:
                    logger.info(f"Deleting ALL predictions for {currency_pair}")

                result = await session.execute(query)
                deleted = result.rowcount
                logger.info(f"Successfully deleted {deleted} predictions for {currency_pair}")
                return deleted

    async def save_model_metrics(
        self,
        model_version: str,
        currency_pair: CurrencyPair,
        mae: float,
        mse: float,
        rmse: float,
        mape: float,
        r2: float,
        training_start_date: date,
        training_end_date: date,
        training_samples: int
    ) -> ModelMetrics:
        """
        Sauvegarder les métriques d'un modèle entraîné

        Returns:
            ModelMetrics créé
        """
        async with self.db_client() as session:
            async with session.begin():
                metrics = ModelMetrics(
                    model_version=model_version,
                    currency_pair=currency_pair,
                    mae=mae,
                    mse=mse,
                    rmse=rmse,
                    mape=mape,
                    r2=r2,
                    training_start_date=training_start_date,
                    training_end_date=training_end_date,
                    training_samples=training_samples
                )

                session.add(metrics)
                await session.flush()
                await session.refresh(metrics)

            return metrics
