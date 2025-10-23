from src.BAM import BankAlMaghribAPI
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()


bam = BankAlMaghribAPI({
    "changes": os.getenv("CLE_API_CHANGES"),
    "bt": os.getenv("CLE_API_BDT"),
    "oblig": os.getenv("CLE_API_OBLIG"),
})

# Récupérer les taux de change
data_fx = bam.get_cours_virement(date="2025-10-08")
print(data_fx)
print()

# Récupérer la courbe des BDT
data_bt = bam.get_courbe_bdt()
print(data_bt)
print()

# Récupérer le marché obligataire
#data_oblig = bam.get_marche_obligataire("2025-10-01")
