"""
BAM API Client
Client pour récupérer les taux de change depuis l'API Bank Al-Maghrib
"""

import requests
import logging
import time
from datetime import datetime, date
from typing import Optional, Dict, Any, List

from exchange_rates.metrics import (
    EXCHANGE_RATE_FETCH_SUCCESS,
    EXCHANGE_RATE_FETCH_ERROR,
    LAST_EXCHANGE_RATE,
    BAM_API_RESPONSE_TIME
)

logger = logging.getLogger(__name__)


class BankAlMaghribAPI:
    """
    Client pour l'API publique de Bank Al-Maghrib (BAM).
    Récupération des cours de change EUR/MAD et USD/MAD
    """

    BASE_URL = "https://api.centralbankofmorocco.ma"

    def __init__(self, api_keys: Dict[str, str]):
        """
        Initialize BAM API client

        Args:
            api_keys: Dictionnaire des clés API
                {
                    "changes": "CLE_API_CHANGES",
                    "changes_2": "CLE_API_CHANGES_2"  # Clé de secours
                }
        """
        self.api_keys = api_keys
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RAG-Finance/1.0',
            'Accept': 'application/json',
            'Cache-Control': 'no-cache'
        })

    def _get(
        self,
        endpoint: str,
        params: Dict[str, Any],
        api_type: str = "changes"
    ) -> Optional[Dict]:
        """
        Effectue une requête GET avec gestion d'erreurs

        Args:
            endpoint: URL de l'endpoint
            params: Paramètres de la requête
            api_type: Type d'API (pour sélectionner la clé)

        Returns:
            Réponse JSON ou None en cas d'erreur
        """
        # Ajouter la clé API
        api_key = self.api_keys.get(api_type)
        if not api_key:
            logger.error(f"API key not found for type: {api_type}")
            return None

        # Bank Al-Maghrib utilise Azure API Management
        headers = {"Ocp-Apim-Subscription-Key": api_key}

        try:
            # Mesurer le temps de réponse de l'API
            start_time = time.time()

            response = self.session.get(
                endpoint,
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # Enregistrer le temps de réponse
            duration = time.time() - start_time
            currency = params.get('libDevise', 'all')
            endpoint_name = 'CoursBBE' if 'CoursBBE' in endpoint else 'CoursVirement'
            BAM_API_RESPONSE_TIME.labels(endpoint=endpoint_name, currency=currency).observe(duration)

            logger.info(f"API request to {endpoint} with params {params} returned: {result}")
            return result

        except requests.exceptions.HTTPError as e:
            # Si c'est une erreur 429, lever l'exception pour permettre le retry dans initial_backfill
            if e.response.status_code == 429:
                logger.warning(f"Rate limit exceeded (429) - will be retried by caller")
                raise  # Lever l'exception pour que initial_backfill.py puisse faire ses retries

            # En cas d'erreur, essayer la clé de secours si disponible
            backup_key = self.api_keys.get(f"{api_type}_2")
            if backup_key and api_key != backup_key:
                logger.warning(f"Primary API key failed, trying backup key")
                headers = {"Ocp-Apim-Subscription-Key": backup_key}
                try:
                    response = self.session.get(
                        endpoint,
                        params=params,
                        headers=headers,
                        timeout=30
                    )
                    response.raise_for_status()
                    return response.json()
                except requests.exceptions.HTTPError as backup_error:
                    # Si la clé de secours a aussi un 429, lever l'exception
                    if backup_error.response.status_code == 429:
                        logger.warning(f"Backup key also rate limited - will be retried by caller")
                        raise  # Lever l'exception pour permettre le retry
                    logger.error(f"Backup API key also failed: {backup_error}")
                    return None
                except Exception as backup_error:
                    logger.error(f"Backup API key also failed: {backup_error}")
                    return None

            logger.error(f"HTTP error fetching data: {e}")
            return None

        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching data from {endpoint}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def get_cours_virement(
        self,
        libDevise: Optional[str] = None,
        date: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Récupérer le cours de virement (transfert)

        Args:
            libDevise: Code devise (ex: "EUR", "USD")
            date: Date au format YYYY-MM-DD

        Returns:
            Données JSON de la réponse ou None
        """
        endpoint = f"{self.BASE_URL}/cours/Version1/api/CoursVirement"
        params = {}

        if libDevise:
            params["libDevise"] = libDevise
        if date:
            params["date"] = date

        return self._get(endpoint, params, api_type="changes")

    def get_cours_billet_banque(
        self,
        libDevise: Optional[str] = None,
        date: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Récupérer le cours des billets de banque

        Args:
            libDevise: Code devise (ex: "EUR", "USD")
            date: Date au format YYYY-MM-DD

        Returns:
            Données JSON de la réponse ou None
        """
        endpoint = f"{self.BASE_URL}/cours/Version1/api/CoursBBE"
        params = {}

        if libDevise:
            params["libDevise"] = libDevise
        if date:
            params["date"] = date

        return self._get(endpoint, params, api_type="changes")

    def get_exchange_rate(
        self,
        devise: str,
        date_obj: Optional[date] = None,
        use_virement: bool = False
    ) -> Optional[Dict[str, float]]:
        """
        Récupérer le taux de change MAD/DEVISE pour une date donnée

        Args:
            devise: Code devise ("EUR" ou "USD")
            date_obj: Date (si None, utilise aujourd'hui)
            use_virement: True pour cours virement, False pour billets (par défaut False car CoursBBE a achat/vente)

        Returns:
            Dict avec {"achat": float, "vente": float} ou None
        """
        if date_obj is None:
            date_obj = datetime.now().date()

        # BAM API requiert le format YYYY-MM-DD
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()

        date_str = date_obj.strftime("%Y-%m-%d")

        # Vérifier si on demande la date du jour
        today = datetime.now().date()
        is_today = (date_obj == today)

        # Choisir le bon endpoint
        # Pour la date du jour, ne pas passer le paramètre date car l'API retourne []
        if use_virement:
            data = self.get_cours_virement(libDevise=devise, date=None if is_today else date_str)
        else:
            data = self.get_cours_billet_banque(libDevise=devise, date=None if is_today else date_str)

        if not data:
            return None

        # Parser la réponse (format réel de l'API BAM)
        try:
            # L'API retourne une liste de dictionnaires
            # Format CoursVirement: [{"date": "...", "libDevise": "EUR", "moyen": 10.4752, "uniteDevise": 1}]
            # Format CoursBBE: [{"date": "...", "libDevise": "EUR", "achatClientele": 10.2153, "venteClientele": 11.8719, "uniteDevise": 1}]

            if isinstance(data, list) and len(data) > 0:
                rate_data = data[0]
            elif isinstance(data, dict):
                rate_data = data
            else:
                logger.warning(f"Unexpected data format: {data}")
                return None

            # CoursBBE retourne achatClientele et venteClientele
            if "achatClientele" in rate_data and "venteClientele" in rate_data:
                achat = float(rate_data.get("achatClientele", 0))
                vente = float(rate_data.get("venteClientele", 0))

                if achat > 0 and vente > 0:
                    moyen = (achat + vente) / 2
                    result = {
                        "achat": round(achat, 4),
                        "vente": round(vente, 4),
                        "moyen": round(moyen, 4)
                    }

                    # Enregistrer le succès et les valeurs dans les métriques
                    EXCHANGE_RATE_FETCH_SUCCESS.labels(
                        currency_pair=f"MAD/{devise}",
                        source="Bank Al-Maghrib API"
                    ).inc()
                    LAST_EXCHANGE_RATE.labels(currency_pair=f"MAD/{devise}", rate_type="achat").set(achat)
                    LAST_EXCHANGE_RATE.labels(currency_pair=f"MAD/{devise}", rate_type="vente").set(vente)
                    LAST_EXCHANGE_RATE.labels(currency_pair=f"MAD/{devise}", rate_type="moyen").set(moyen)

                    return result

            # CoursVirement retourne seulement le taux moyen
            elif "moyen" in rate_data:
                moyen = float(rate_data.get("moyen", 0))

                if moyen > 0:
                    # Estimation: spread de ±0.5% autour du taux moyen
                    spread_pct = 0.005
                    achat = moyen * (1 - spread_pct)
                    vente = moyen * (1 + spread_pct)
                    result = {
                        "achat": round(achat, 4),
                        "vente": round(vente, 4),
                        "moyen": moyen
                    }

                    # Enregistrer le succès et les valeurs dans les métriques
                    EXCHANGE_RATE_FETCH_SUCCESS.labels(
                        currency_pair=f"MAD/{devise}",
                        source="Bank Al-Maghrib API"
                    ).inc()
                    LAST_EXCHANGE_RATE.labels(currency_pair=f"MAD/{devise}", rate_type="achat").set(achat)
                    LAST_EXCHANGE_RATE.labels(currency_pair=f"MAD/{devise}", rate_type="vente").set(vente)
                    LAST_EXCHANGE_RATE.labels(currency_pair=f"MAD/{devise}", rate_type="moyen").set(moyen)

                    return result

            logger.warning(f"Invalid rate data (missing required fields): {rate_data}")
            EXCHANGE_RATE_FETCH_ERROR.labels(
                currency_pair=f"MAD/{devise}",
                error_type="invalid_data"
            ).inc()
            return None

        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing exchange rate data: {e}")
            logger.debug(f"Raw data: {data}")
            EXCHANGE_RATE_FETCH_ERROR.labels(
                currency_pair=f"MAD/{devise}",
                error_type="parse_error"
            ).inc()
            return None

    def get_eur_mad_rate(self, date_obj: Optional[date] = None) -> Optional[Dict[str, float]]:
        """Récupérer le taux EUR/MAD"""
        return self.get_exchange_rate("EUR", date_obj)

    def get_usd_mad_rate(self, date_obj: Optional[date] = None) -> Optional[Dict[str, float]]:
        """Récupérer le taux USD/MAD"""
        return self.get_exchange_rate("USD", date_obj)

    def get_both_rates(self, date_obj: Optional[date] = None) -> Dict[str, Optional[Dict[str, float]]]:
        """
        Récupérer EUR/MAD et USD/MAD en une fois

        Returns:
            {
                "EUR/MAD": {"achat": float, "vente": float},
                "USD/MAD": {"achat": float, "vente": float}
            }
        """
        return {
            "EUR/MAD": self.get_eur_mad_rate(date_obj),
            "USD/MAD": self.get_usd_mad_rate(date_obj)
        }
