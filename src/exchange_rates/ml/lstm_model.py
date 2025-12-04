"""
LSTM Model for Exchange Rate Prediction
Modèle de Deep Learning pour prédire les taux de change
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Optional
from datetime import datetime, timedelta
import logging
import joblib
from pathlib import Path

try:
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
except ImportError:
    keras = None
    LSTM = None
    logging.warning("TensorFlow not installed. LSTM model will not be available.")

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error

logger = logging.getLogger(__name__)


class ExchangeRateLSTM:
    """
    Modèle LSTM pour prédire les taux de change
    """

    def __init__(
        self,
        sequence_length: int = 30,  # 30 jours d'historique pour prédire
        prediction_horizon: int = 7,  # Prédire 7 jours dans le futur
        lstm_units: int = 50,
        dropout_rate: float = 0.2
    ):
        """
        Initialize LSTM model

        Args:
            sequence_length: Nombre de jours passés à utiliser pour la prédiction
            prediction_horizon: Nombre de jours à prédire dans le futur
            lstm_units: Nombre d'unités dans les couches LSTM
            dropout_rate: Taux de dropout pour régularisation
        """
        if keras is None:
            raise ImportError("TensorFlow is required for LSTM model. Install with: pip install tensorflow")

        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate

        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.is_trained = False

    def build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """
        Construire l'architecture du modèle LSTM

        Args:
            input_shape: (sequence_length, n_features)

        Returns:
            Modèle Keras compilé
        """
        model = Sequential([
            # Première couche LSTM
            LSTM(
                units=self.lstm_units,
                return_sequences=True,
                input_shape=input_shape
            ),
            Dropout(self.dropout_rate),

            # Deuxième couche LSTM
            LSTM(
                units=self.lstm_units // 2,
                return_sequences=False
            ),
            Dropout(self.dropout_rate),

            # Couche Dense
            Dense(units=25, activation='relu'),
            Dropout(self.dropout_rate),

            # Couche de sortie
            Dense(units=self.prediction_horizon)  # Prédire N jours
        ])

        model.compile(
            optimizer='adam',
            loss='mean_squared_error',
            metrics=['mean_absolute_error']
        )

        return model

    def prepare_data(
        self,
        historical_rates: pd.DataFrame,
        target_column: str = 'moyenne',
        fill_missing: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Préparer les données pour l'entraînement
        Gère les données manquantes (weekends, jours fériés)

        Args:
            historical_rates: DataFrame avec colonnes ['date', 'achat', 'vente', 'moyenne']
            target_column: Colonne à prédire (par défaut 'moyenne')
            fill_missing: Si True, remplit les jours manquants par interpolation

        Returns:
            (X_train, y_train, scaled_data)
        """
        # Trier par date
        df = historical_rates.sort_values('date').copy()

        if fill_missing and len(df) > 0:
            # Créer un index de dates complet (tous les jours)
            date_range = pd.date_range(
                start=df['date'].min(),
                end=df['date'].max(),
                freq='D'
            )

            # Réindexer pour avoir tous les jours
            df = df.set_index('date')
            df = df.reindex(date_range)

            # Interpoler les valeurs manquantes (méthode linéaire)
            df[target_column] = df[target_column].interpolate(method='linear', limit_direction='both')

            # Si des valeurs manquent toujours (début/fin), forward/backward fill
            df[target_column] = df[target_column].ffill().bfill()

            df = df.reset_index()
            df.rename(columns={'index': 'date'}, inplace=True)

            logger.info(f"Filled missing days: {len(df)} total days (from {len(historical_rates)} available)")

        # Extraire les valeurs à prédire
        data = df[target_column].values.reshape(-1, 1)

        # Normaliser les données
        scaled_data = self.scaler.fit_transform(data)

        # Créer les séquences
        X, y = [], []

        for i in range(self.sequence_length, len(scaled_data) - self.prediction_horizon + 1):
            # X: sequence_length jours passés
            X.append(scaled_data[i - self.sequence_length:i, 0])

            # y: prediction_horizon jours futurs
            y.append(scaled_data[i:i + self.prediction_horizon, 0])

        X = np.array(X)
        y = np.array(y)

        # Reshape pour LSTM (samples, timesteps, features)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))

        return X, y, scaled_data

    def train(
        self,
        historical_rates: pd.DataFrame,
        validation_split: float = 0.2,
        epochs: int = 100,
        batch_size: int = 32,
        verbose: int = 1
    ) -> dict:
        """
        Entraîner le modèle

        Args:
            historical_rates: Données historiques
            validation_split: Pourcentage de données pour validation
            epochs: Nombre d'époques d'entraînement
            batch_size: Taille des batchs
            verbose: Niveau de verbosité

        Returns:
            Historique d'entraînement et métriques
        """
        logger.info(f"Training LSTM model with {len(historical_rates)} data points")

        # Préparer les données
        X, y, scaled_data = self.prepare_data(historical_rates)

        # Construire le modèle
        self.model = self.build_model(input_shape=(X.shape[1], X.shape[2]))

        # Callbacks
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True
        )

        # Entraîner
        history = self.model.fit(
            X, y,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping],
            verbose=verbose
        )

        self.is_trained = True

        # Calculer les métriques finales
        y_pred = self.model.predict(X, verbose=0)
        y_pred_original = self.scaler.inverse_transform(y_pred)
        y_true_original = self.scaler.inverse_transform(y)

        metrics = {
            'mae': float(mean_absolute_error(y_true_original.flatten(), y_pred_original.flatten())),
            'mse': float(mean_squared_error(y_true_original.flatten(), y_pred_original.flatten())),
            'rmse': float(np.sqrt(mean_squared_error(y_true_original.flatten(), y_pred_original.flatten()))),
            'mape': float(mean_absolute_percentage_error(y_true_original.flatten(), y_pred_original.flatten())),
            'epochs_trained': len(history.history['loss']),
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1])
        }

        logger.info(f"Training complete. MAE: {metrics['mae']:.4f}, RMSE: {metrics['rmse']:.4f}")

        return metrics

    def predict(
        self,
        recent_data: pd.DataFrame,
        target_column: str = 'moyenne',
        fill_missing: bool = True
    ) -> np.ndarray:
        """
        Faire des prédictions pour les prochains jours
        Gère les données manquantes (weekends, jours fériés)

        Args:
            recent_data: Derniers jours de données (min sequence_length jours disponibles)
            target_column: Colonne à prédire
            fill_missing: Si True, remplit les jours manquants par interpolation

        Returns:
            Array de prédictions pour les N prochains jours
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Model must be trained before prediction")

        # Trier par date
        df = recent_data.sort_values('date').copy()

        # Vérifier qu'on a assez de données DISPONIBLES (pas nécessairement consécutives)
        if len(df) < self.sequence_length:
            raise ValueError(
                f"Need at least {self.sequence_length} days of available data for prediction. "
                f"Got {len(df)} days. Missing data will be filled by interpolation."
            )

        if fill_missing and len(df) > 0:
            # Créer un index de dates complet jusqu'à aujourd'hui
            # On prend les N derniers jours calendaires pour avoir sequence_length jours de données
            end_date = df['date'].max()
            # Calculer combien de jours calendaires on a besoin pour avoir sequence_length jours ouvrables
            # En moyenne, 5 jours ouvrables = 7 jours calendaires
            # Donc pour avoir sequence_length jours ouvrables, on prend ~1.4x jours calendaires
            calendar_days_needed = int(self.sequence_length * 1.5)
            start_date = end_date - timedelta(days=calendar_days_needed)

            # S'assurer qu'on ne commence pas avant les données disponibles
            if start_date < df['date'].min():
                start_date = df['date'].min()

            # Créer la plage de dates complète
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')

            # Réindexer
            df = df.set_index('date')
            df = df.reindex(date_range)

            # Interpoler les valeurs manquantes
            df[target_column] = df[target_column].interpolate(method='linear', limit_direction='both')
            df[target_column] = df[target_column].ffill().bfill()

            df = df.reset_index()
            df.rename(columns={'index': 'date'}, inplace=True)

            logger.debug(f"Filled missing days for prediction: {len(df)} total days")

        # Prendre les derniers sequence_length jours
        df = df.tail(self.sequence_length)
        data = df[target_column].values.reshape(-1, 1)

        # Normaliser
        scaled_data = self.scaler.transform(data)

        # Créer la séquence d'entrée
        X = np.array([scaled_data[:, 0]])
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))

        # Prédire
        predictions_scaled = self.model.predict(X, verbose=0)

        # Dénormaliser
        predictions = self.scaler.inverse_transform(predictions_scaled)

        return predictions[0]

    def save(self, filepath: str):
        """Sauvegarder le modèle et le scaler"""
        if self.model is None:
            raise ValueError("No model to save")

        # Sauvegarder le modèle Keras
        self.model.save(filepath)

        # Sauvegarder le scaler avec joblib
        scaler_path = Path(filepath).with_suffix('.scaler.pkl')
        joblib.dump(self.scaler, scaler_path)

        logger.info(f"Model saved to {filepath}")
        logger.info(f"Scaler saved to {scaler_path}")

    def load(self, filepath: str):
        """Charger un modèle sauvegardé et son scaler"""
        # Charger le modèle Keras
        self.model = load_model(filepath)

        # Charger le scaler avec joblib
        scaler_path = Path(filepath).with_suffix('.scaler.pkl')
        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
            logger.info(f"Scaler loaded from {scaler_path}")
        else:
            logger.warning(f"Scaler file not found at {scaler_path}. Using default scaler.")
            logger.warning("You may need to retrain the model to generate the scaler file.")

        self.is_trained = True
        logger.info(f"Model loaded from {filepath}")

    def get_model_summary(self) -> str:
        """Obtenir un résumé du modèle"""
        if self.model is None:
            return "Model not built yet"

        summary_list = []
        self.model.summary(print_fn=lambda x: summary_list.append(x))
        return "\n".join(summary_list)
