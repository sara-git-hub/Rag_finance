"""
Prediction Service
Service pour gérer l'entraînement et les prédictions des taux de change
"""

import pandas as pd
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from exchange_rates.ml.lstm_model import ExchangeRateLSTM
from exchange_rates.models.ExchangeRateModel import ExchangeRateModel
from exchange_rates.metrics import (
    PREDICTION_GENERATED,
    PREDICTION_ERROR,
    MODEL_ACCURACY_METRICS
)
from models.db_schemes import CurrencyPair, RateType

logger = logging.getLogger(__name__)


class PredictionService:
    """Service pour générer des prédictions de taux de change"""

    def __init__(
        self,
        db_client,
        models_dir: str = "models/exchange_rates"
    ):
        """
        Initialize Prediction Service

        Args:
            db_client: Database client
            models_dir: Répertoire pour sauvegarder les modèles
        """
        self.db_client = db_client
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Cache des modèles
        self.lstm_models: Dict[str, ExchangeRateLSTM] = {}

    def _get_model_path(self, currency_pair: CurrencyPair, version: str = "v1") -> Path:
        """Obtenir le chemin du fichier modèle"""
        pair_name = currency_pair.value.replace("/", "_")
        return self.models_dir / f"lstm_{pair_name}_{version}.h5"

    async def train_model(
        self,
        currency_pair: CurrencyPair,
        days_history: int = 365,
        sequence_length: int = 30,
        prediction_horizon: int = 7,
        force_retrain: bool = False
    ) -> Dict:
        """
        Entraîner un modèle LSTM pour une paire de devises

        Args:
            currency_pair: Paire de devises
            days_history: Nombre de jours d'historique à utiliser
            sequence_length: Longueur de séquence pour LSTM
            prediction_horizon: Jours à prédire
            force_retrain: Forcer le ré-entraînement même si modèle existe

        Returns:
            Métriques et informations sur l'entraînement
        """
        logger.info(f"Training model for {currency_pair.value}")

        # Récupérer les données historiques
        model = await ExchangeRateModel.create_instance(self.db_client)
        historical_data = await model.get_historical_data(
            currency_pair=currency_pair,
            days=days_history,
            rate_type=RateType.ACTUAL
        )

        if len(historical_data) < sequence_length + prediction_horizon:
            raise ValueError(
                f"Not enough historical data. Need at least {sequence_length + prediction_horizon} days, "
                f"got {len(historical_data)}"
            )

        # Convertir en DataFrame
        df = pd.DataFrame([
            {
                'date': rate.date,
                'achat': rate.achat,
                'vente': rate.vente,
                'moyenne': rate.moyenne
            }
            for rate in historical_data
        ])

        logger.info(f"Using {len(df)} days of historical data for training")

        # Créer et entraîner le modèle LSTM
        lstm = ExchangeRateLSTM(
            sequence_length=sequence_length,
            prediction_horizon=prediction_horizon
        )

        metrics = lstm.train(
            historical_rates=df,
            validation_split=0.2,
            epochs=100,
            batch_size=32,
            verbose=0
        )

        # Sauvegarder le modèle
        model_path = self._get_model_path(currency_pair)
        lstm.save(str(model_path))

        # Cacher le modèle
        self.lstm_models[currency_pair.value] = lstm

        # Sauvegarder les métriques en DB
        await model.save_model_metrics(
            model_version="lstm_v1.0",
            currency_pair=currency_pair,
            mae=metrics['mae'],
            mse=metrics['mse'],
            rmse=metrics['rmse'],
            mape=metrics['mape'],
            training_start_date=df['date'].min(),
            training_end_date=df['date'].max(),
            training_samples=len(df)
        )

        # Enregistrer les métriques dans Prometheus
        MODEL_ACCURACY_METRICS.labels(
            currency_pair=currency_pair.value,
            metric_type="mae"
        ).set(metrics['mae'])
        MODEL_ACCURACY_METRICS.labels(
            currency_pair=currency_pair.value,
            metric_type="mse"
        ).set(metrics['mse'])
        MODEL_ACCURACY_METRICS.labels(
            currency_pair=currency_pair.value,
            metric_type="rmse"
        ).set(metrics['rmse'])
        MODEL_ACCURACY_METRICS.labels(
            currency_pair=currency_pair.value,
            metric_type="mape"
        ).set(metrics['mape'])

        logger.info(f"Model trained and saved to {model_path}")

        return {
            'success': True,
            'currency_pair': currency_pair.value,
            'model_path': str(model_path),
            'metrics': metrics,
            'training_samples': len(df),
            'date_range': {
                'start': df['date'].min().isoformat(),
                'end': df['date'].max().isoformat()
            }
        }

    def _load_model(self, currency_pair: CurrencyPair) -> ExchangeRateLSTM:
        """
        Charger un modèle depuis le cache ou le disque

        Args:
            currency_pair: Paire de devises

        Returns:
            Modèle LSTM chargé
        """
        # Vérifier le cache
        if currency_pair.value in self.lstm_models:
            return self.lstm_models[currency_pair.value]

        # Charger depuis le disque
        model_path = self._get_model_path(currency_pair)

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model for {currency_pair.value} not found. Please train the model first."
            )

        lstm = ExchangeRateLSTM()
        lstm.load(str(model_path))

        # Mettre en cache
        self.lstm_models[currency_pair.value] = lstm

        return lstm

    async def generate_predictions(
        self,
        currency_pair: CurrencyPair,
        days_ahead: int = 7
    ) -> List[Dict]:
        """
        Générer des prédictions pour les prochains jours

        Args:
            currency_pair: Paire de devises
            days_ahead: Nombre de jours à prédire

        Returns:
            Liste de prédictions avec dates et valeurs
        """
        logger.info(f"Generating predictions for {currency_pair.value}")

        # Charger le modèle
        lstm = self._load_model(currency_pair)

        # Récupérer les données récentes
        model = await ExchangeRateModel.create_instance(self.db_client)
        recent_data = await model.get_historical_data(
            currency_pair=currency_pair,
            days=lstm.sequence_length + 30,  # Un peu plus pour être sûr
            rate_type=RateType.ACTUAL
        )

        if len(recent_data) < lstm.sequence_length:
            raise ValueError(f"Not enough recent data for prediction")

        # Convertir en DataFrame
        df = pd.DataFrame([
            {
                'date': rate.date,
                'achat': rate.achat,
                'vente': rate.vente,
                'moyenne': rate.moyenne
            }
            for rate in recent_data
        ])

        # Faire les prédictions
        predictions = lstm.predict(df)

        # Créer les dates futures
        last_date = df['date'].max()
        prediction_dates = [
            last_date + timedelta(days=i+1)
            for i in range(min(days_ahead, len(predictions)))
        ]

        # Formatter les résultats
        results = []
        for pred_date, pred_value in zip(prediction_dates, predictions[:days_ahead]):
            results.append({
                'date': pred_date,
                'predicted_moyenne': float(pred_value),
                'currency_pair': currency_pair.value
            })

        # Enregistrer dans les métriques Prometheus
        PREDICTION_GENERATED.labels(
            currency_pair=currency_pair.value,
            model_version="lstm_v1.0"
        ).inc(len(results))

        logger.info(f"Generated {len(results)} predictions")

        return results

    async def save_predictions_to_db(
        self,
        currency_pair: CurrencyPair,
        days_ahead: int = 7
    ) -> int:
        """
        Générer et sauvegarder les prédictions en base de données

        Args:
            currency_pair: Paire de devises
            days_ahead: Nombre de jours à prédire

        Returns:
            Nombre de prédictions sauvegardées
        """
        # Supprimer TOUTES les anciennes prédictions (passées et futures)
        model = await ExchangeRateModel.create_instance(self.db_client)
        deleted_count = await model.delete_predictions(
            currency_pair=currency_pair,
            start_date=None  # None = supprimer toutes les prédictions
        )
        logger.info(f"Deleted {deleted_count} old predictions for {currency_pair.value}")

        # Générer les nouvelles prédictions
        predictions = await self.generate_predictions(currency_pair, days_ahead)

        # Sauvegarder les nouvelles prédictions
        rates_to_insert = []
        for pred in predictions:
            # Utiliser la moyenne pour achat et vente (simplification)
            # Dans une version plus sophistiquée, on pourrait prédire les deux séparément
            rates_to_insert.append({
                'currency_pair': currency_pair,
                'date': pred['date'],
                'achat': pred['predicted_moyenne'],
                'vente': pred['predicted_moyenne'],
                'rate_type': RateType.PREDICTED,
                'source': 'LSTM Model v1.0',
                'confidence_score': 0.85  # Pourrait être calculé dynamiquement
            })

        count = await model.insert_rates_batch(rates_to_insert)

        logger.info(f"Saved {count} predictions to database")

        return count

    async def get_predictions_with_history(
        self,
        currency_pair: CurrencyPair,
        history_days: int = 30,
        prediction_days: int = 7
    ) -> Dict:
        """
        Récupérer l'historique et les prédictions pour visualisation

        Args:
            currency_pair: Paire de devises
            history_days: Jours d'historique à inclure
            prediction_days: Jours de prédictions à inclure

        Returns:
            Dict avec historique et prédictions
        """
        model = await ExchangeRateModel.create_instance(self.db_client)

        # Récupérer l'historique
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=history_days)

        historical = await model.get_rates_by_date_range(
            currency_pair=currency_pair,
            start_date=start_date,
            end_date=end_date,
            rate_type=RateType.ACTUAL
        )

        # Récupérer les prédictions
        predictions_start = end_date + timedelta(days=1)
        predictions_end = end_date + timedelta(days=prediction_days)

        predicted = await model.get_rates_by_date_range(
            currency_pair=currency_pair,
            start_date=predictions_start,
            end_date=predictions_end,
            rate_type=RateType.PREDICTED
        )

        return {
            'currency_pair': currency_pair.value,
            'historical': [
                {
                    'date': rate.date.isoformat(),
                    'achat': rate.achat,
                    'vente': rate.vente,
                    'moyenne': rate.moyenne,
                    'type': 'actual'
                }
                for rate in historical
            ],
            'predictions': [
                {
                    'date': rate.date.isoformat(),
                    'predicted_moyenne': rate.moyenne,
                    'confidence_score': rate.confidence_score,
                    'type': 'predicted'
                }
                for rate in predicted
            ]
        }
