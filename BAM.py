import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class BankAlMaghribAPI:
    """
    Client pour l'API publique de Bank Al-Maghrib (BAM).
    Chaque domaine (marché des changes, bons du trésor, marché obligataire)
    possède sa propre clé API.
    """

    BASE_URL = "https://api.centralbankofmorocco.ma"

    def __init__(self, api_keys: Dict[str, str]):
        """
        api_keys = {
            "changes": "CLE_API_CHANGES",
            "bt": "CLE_API_BONS_TRESOR",
            "oblig": "CLE_API_MARCHE_OBLIGATAIRE"
        }
        """
        self.api_keys = api_keys

    # --------------------------
    # 1️⃣ Marché des changes
    # --------------------------
    def get_cours_virement(self, libDevise:Optional[str] = None,date: Optional[str] = None):
        endpoint = f"{self.BASE_URL}/cours/Version1/api/CoursVirement"
        params = {}
        if libDevise:
            params["libDevise"] = libDevise
        if date:
            params["date"] = date
        return self._get(endpoint, params , api_type="changes")

    def get_cours_billet_banque(self, libDevise:Optional[str] = None, date: Optional[str] = None):
        endpoint = f"{self.BASE_URL}/cours/Version1/api/CoursBBE"
        params = {}
        if libDevise:
            params["libDevise"] = libDevise
        if date:
            params["date"] = date
        return self._get(endpoint, params , api_type="changes")

    # --------------------------
    # 2️⃣ Marché obligataire
    # --------------------------
    def get_courbe_bdt(self, dateCourbe: Optional[str] = None):
        endpoint = f"{self.BASE_URL}/mo/Version1/api/CourbeBDT"
        params = {"dateCourbe": dateCourbe or datetime.now().strftime("%Y-%m-%d")}
        return self._get(endpoint, params, api_type="oblig")


    # --------------------------
    # ⚙️ Méthode générique
    # --------------------------
    def _get(self, endpoint: str, params: Dict[str, Any], api_type: str):
        api_key = self.api_keys.get(api_type)
        if not api_key:
            raise ValueError(f"Aucune clé API fournie pour le domaine : {api_type}")

        headers = {
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": self.api_keys.get(api_type, "")
        }

        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur API BAM ({api_type}) : {e}")
            return {"error": str(e)}
        
        
    # --------------------------
    # 3️⃣ Bons du Trésor 
    # --------------------------
    ''' def get_marche_obligataire(self, dateAdjudicationDu: [str] = None):
        endpoint = f"{self.BASE_URL}/adju/Version1/api/GenTELADJ[?dateAdjudicationDu][&dateAdjudicationAu][&instrument]"
        params = {"date": dateAdjudicationDu or datetime.now().strftime("%Y-%m-%d")}
        return self._get(endpoint, params, api_type="bt")'''