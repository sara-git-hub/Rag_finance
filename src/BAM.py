"""
BAM API Client
Client pour récupérer les taux de change depuis l'API Bank Al-Maghrib
"""

import requests
import logging
from datetime import datetime, date
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class BankAlMaghribAPI:
    """
    Client pour l'API publique de Bank Al-Maghrib (BAM).
    Récupération des cours de change MAD/EUR et MAD/USD
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
            response = self.session.get(
                endpoint,
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
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

        # BAM API requiert le format DD/MM/YYYY
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()

        date_str = date_obj.strftime("%d/%m/%Y")

        # Choisir le bon endpoint
        if use_virement:
            data = self.get_cours_virement(libDevise=devise, date=date_str)
        else:
            data = self.get_cours_billet_banque(libDevise=devise, date=date_str)

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
                    return {
                        "achat": round(achat, 4),
                        "vente": round(vente, 4),
                        "moyen": round(moyen, 4)
                    }

            # CoursVirement retourne seulement le taux moyen
            elif "moyen" in rate_data:
                moyen = float(rate_data.get("moyen", 0))

                if moyen > 0:
                    # Estimation: spread de ±0.5% autour du taux moyen
                    spread_pct = 0.005
                    achat = moyen * (1 - spread_pct)
                    vente = moyen * (1 + spread_pct)
                    return {
                        "achat": round(achat, 4),
                        "vente": round(vente, 4),
                        "moyen": moyen
                    }

            logger.warning(f"Invalid rate data (missing required fields): {rate_data}")
            return None

        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing exchange rate data: {e}")
            logger.debug(f"Raw data: {data}")
            return None

    def get_mad_eur_rate(self, date_obj: Optional[date] = None) -> Optional[Dict[str, float]]:
        """Récupérer le taux MAD/EUR"""
        return self.get_exchange_rate("EUR", date_obj)

    def get_mad_usd_rate(self, date_obj: Optional[date] = None) -> Optional[Dict[str, float]]:
        """Récupérer le taux MAD/USD"""
        return self.get_exchange_rate("USD", date_obj)

    def get_both_rates(self, date_obj: Optional[date] = None) -> Dict[str, Optional[Dict[str, float]]]:
        """
        Récupérer MAD/EUR et MAD/USD en une fois

        Returns:
            {
                "MAD/EUR": {"achat": float, "vente": float},
                "MAD/USD": {"achat": float, "vente": float}
            }
        """
        return {
            "MAD/EUR": self.get_mad_eur_rate(date_obj),
            "MAD/USD": self.get_mad_usd_rate(date_obj)
        }

